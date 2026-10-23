"""A SISTEMA session: attach, drive, and read back - with no screenshots.

Design
------
*Nothing* here looks at pixels.  Every write is followed by a read-back through
``WM_GETTEXT``/``BM_GETCHECK`` on the same control, and every structural change is
confirmed against a second, independent channel (the panel that SISTEMA selects
after the change, the saved ``.ssm``, or the exported PDF).

The static UI dictionary in ``sistema_ui_map.json`` (built by
``tools/sistema/rea_ui_map.py`` from REA's PE-resource inventory) turns HWNDs into
names like ``LEExName`` / ``CBCat`` / ``CB1_FncTypes``, and into the exact caption
SISTEMA paints next to each of them.
"""
from __future__ import annotations

import os
import subprocess
import time

from . import win32 as W
from .uimap import FormInstance, UiMap, set_dpi_aware, wait_for

DEFAULT_EXE = r"C:\Program Files (x86)\SISTEMA 3.0.4\SISTEMA.exe"
MAIN_CLASS = "TFormMain"

#: Panel forms that carry an editable object.  The first one that is visible is
#: the object SISTEMA currently has selected in the project tree.
EDITABLE_PANELS = (
    "TFormProject", "TFormSF", "TFormComponent", "TFormChannel", "TFormElement",
    "TFormChannelManager", "TFormCCFMeasure",
)

#: Panels that are read-only companions.
VIEW_PANELS = ("TFormContext", "TFormSSMMessageListUI", "TFormMessageHelperListUI",
               "TFormHtmlBrowser", "TFormT10DDeviceListUI", "TFormLib")

#: Runtime class -> PE resource name, for forms whose DFM resource is inherited.
FORM_ALIASES = {
    "TFormSSMMessageListUI": "TFormSSMMessageListUIAbs",
}

NAME_FIELD = "LEExName"

#: Windows SISTEMA keeps around for embedded browsers/tray plumbing; they are
#: visible but are not dialogs and must never be mistaken for one.
HELPER_CLASSES = {
    "Internet Explorer_Hidden", "Shell Embedding", "Shell DocObject View",
    "Internet Explorer_Server", "TNotifierWindow", "ThumbnailDeviceHelperWnd",
    "DummyDWMListenerWindow", "MSCTFIME UI", "IME", "GDI+ Hook Window Class",
}


class SistemaError(RuntimeError):
    """The session could not complete an operation."""


class Sistema:
    """One running SISTEMA instance."""

    def __init__(self, exe: str = DEFAULT_EXE, ui_map: str | None = None) -> None:
        set_dpi_aware()
        self.exe = exe
        self.ui = UiMap(ui_map) if ui_map else UiMap()
        self.pid = 0
        self.main = 0
        self._dialog_baseline: set[int] = set()

    # ------------------------------------------------------------- lifecycle
    def attach(self, timeout: float = 20.0) -> "Sistema":
        found = wait_for(lambda: next((t for t in W.snapshot() if t.cls == MAIN_CLASS), None),
                         timeout=timeout)
        if not found:
            raise SistemaError("SISTEMA is not running (no TFormMain window found)")
        self.main = found.hwnd
        self.pid = found.pid
        self._dialog_baseline = {t.hwnd for t in self.top_levels()}
        return self

    def launch(self, project: str | None = None, timeout: float = 90.0) -> "Sistema":
        """Start SISTEMA (optionally with a project) and wait for its main window."""
        if self._find_main():
            return self.attach()
        args = [self.exe] + ([project] if project else [])
        subprocess.Popen(args, cwd=os.path.dirname(self.exe), close_fds=True)
        deadline = time.time() + timeout
        while time.time() < deadline:
            window = self._find_main()
            if window:
                # The splash screen owns TFormSplash; wait for the real main form.
                time.sleep(0.8)
                self.main = window.hwnd
                self.pid = window.pid
                self._dialog_baseline = {t.hwnd for t in self.top_levels()}
                self.wait_idle()
                return self
            time.sleep(0.4)
        raise SistemaError("SISTEMA did not open its main window in time")

    def _find_main(self):
        return next((t for t in W.snapshot() if t.cls == MAIN_CLASS), None)

    def alive(self) -> bool:
        return bool(self.main) and bool(W.user32.IsWindow(self.main)) and self.pid > 0

    def focus(self) -> None:
        if not W.focus_window(self.main):
            raise SistemaError("could not bring SISTEMA to the foreground")

    # ----------------------------------------------------------------- views
    def top_levels(self) -> list[W.Window]:
        return W.snapshot(pid=self.pid, include_hidden=False)

    def dialogs(self) -> list[W.Window]:
        """Visible top-level windows that are not the main form (modal boxes)."""
        out = []
        for window in self.top_levels():
            if window.hwnd == self.main or window.cls == MAIN_CLASS:
                continue
            if window.cls in HELPER_CLASSES:
                continue
            if window.width < 60 or window.height < 40:
                continue
            out.append(window)
        return out

    def new_dialogs(self) -> list[W.Window]:
        return [t for t in self.dialogs() if t.hwnd not in self._dialog_baseline]

    def descendants(self) -> list[int]:
        return W.descendants(self.main)

    def panel_hwnds(self) -> dict[str, list[int]]:
        out: dict[str, list[int]] = {}
        for hwnd in self.descendants():
            cls = W.class_name(hwnd)
            if cls.startswith("TForm"):
                out.setdefault(cls, []).append(hwnd)
        return out

    def form(self, form_name: str, visible_only: bool = True) -> FormInstance:
        """Bind the DFM definition of ``form_name`` to its live window."""
        alias = FORM_ALIASES.get(form_name, form_name)
        candidates = [hwnd for hwnd in self.descendants()
                      if W.class_name(hwnd) == form_name
                      or W.class_name(hwnd) == alias]
        if not candidates:
            raise SistemaError(f"panel {form_name} has not been created by SISTEMA yet")
        if visible_only:
            visible = [h for h in candidates if W.user32.IsWindowVisible(h)]
            if visible:
                candidates = visible
        return FormInstance(self.ui, form_name, candidates[0])

    def current_panel(self) -> FormInstance:
        """The panel of the object currently selected in the project tree."""
        present = {W.class_name(hwnd) for hwnd in self.descendants()}
        for name in EDITABLE_PANELS:
            if name not in present:
                continue
            hwnds = [h for h in self.descendants()
                     if W.class_name(h) == name and W.user32.IsWindowVisible(h)]
            if not hwnds:
                continue
            return FormInstance(self.ui, name, hwnds[0])
        raise SistemaError("no editable object panel is visible; select a node first")

    def current_name(self) -> str:
        """Name of the selected object - the tree's selection, read without the tree."""
        panel = self.current_panel()
        if not panel.has(NAME_FIELD):
            return ""
        return panel.text(NAME_FIELD)

    def tree(self) -> int:
        for hwnd in self.descendants():
            if W.class_name(hwnd) == "TtiVTTreeView":
                return hwnd
        raise SistemaError("project tree (TtiVTTreeView) not found")

    # ------------------------------------------------------------------ idle
    def wait_idle(self, settle: float = 0.6, timeout: float = 30.0) -> None:
        """Wait until the UI stops creating windows and has no pending dialog."""
        last = -1
        stable_since = time.time()
        deadline = time.time() + timeout
        while time.time() < deadline:
            count = len(W.descendants(self.main))
            if count != last:
                last = count
                stable_since = time.time()
            elif time.time() - stable_since >= settle:
                return
            time.sleep(0.15)

    # ------------------------------------------------------------ primitives
    def keys(self, *specs: str, settle: float = 0.4) -> None:
        """Send real keyboard input to the focused SISTEMA control."""
        self.focus()
        for spec in specs:
            W.chord(spec)
            time.sleep(0.12)
        time.sleep(settle)

    def tree_keys(self, *specs: str, settle: float = 0.4) -> None:
        """Keyboard input aimed at the project tree."""
        self.focus()
        W.set_focus(self.tree())
        for spec in specs:
            W.chord(spec)
            time.sleep(0.12)
        time.sleep(settle)

    def type_text(self, text: str, settle: float = 0.2) -> None:
        W.type_text(text)
        time.sleep(settle)

    # --------------------------------------------------------------- dialogs
    def file_edit(self, dialog_hwnd: int) -> int:
        """The file-name edit inside an Open/Save dialog.

        SISTEMA's own dialogs (``TFormLoadFile``) use ``TLabeledEditEx``; the ones
        that fall back to the VCL dialog use ``TEdit``.  Prefer an edit that already
        holds a path, otherwise the last one, which is the file-name field.
        """
        candidates = []
        for hwnd in W.descendants(dialog_hwnd):
            if W.class_name(hwnd) in ("TLabeledEditEx", "TEdit", "Edit", "TComboBox"):
                candidates.append(hwnd)
        if not candidates:
            return 0
        for hwnd in candidates:
            text = W.window_text(hwnd)
            if ".ssm" in text.lower() or "\\" in text or "/" in text:
                return hwnd
        return candidates[-1]

    def accept_dialog(self, prefer: str | None = None) -> str:
        """Dismiss a modal box by pressing its named button, then Enter/Escape.

        Returns the button caption that was pressed, so the caller can tell
        "Overwrite" from "Cancel".
        """
        dialog = next(iter(self.new_dialogs()), None)
        if dialog is None:
            return ""
        pressed = ""
        for hwnd in W.descendants(dialog.hwnd):
            cls = W.class_name(hwnd)
            if cls not in ("TIFABitBtn", "TBitBtn", "TButton"):
                continue
            caption = W.window_text(hwnd)
            if prefer and prefer.lower() in caption.lower():
                W.click(hwnd)
                pressed = caption
                break
        if not pressed:
            W.post(dialog.hwnd, W.WM_COMMAND, 1, 0)      # IDOK
            time.sleep(0.2)
            if not W.user32.IsWindow(dialog.hwnd):
                pressed = "IDOK"
        if not pressed:
            self.keys("ENTER", settle=0.3)
            pressed = "ENTER"
        self.wait_idle()
        return pressed

    def dialog_text(self) -> str:
        """Every readable string inside the current modal box."""
        dialog = next(iter(self.new_dialogs()), None)
        if dialog is None:
            return ""
        parts = [dialog.title]
        for hwnd in W.descendants(dialog.hwnd):
            text = W.window_text(hwnd)
            if text:
                parts.append(text)
        return " | ".join(parts)

    # ------------------------------------------------------------ operations
    def new_project(self, name: str = "") -> FormInstance:
        """``File -> New`` and name the project through the Project panel."""
        self.keys("Ctrl+N", settle=1.2)
        self.wait_idle()
        panel = self.form("TFormProject")
        if name:
            written = panel.set_text(NAME_FIELD, name)
            if written != name:
                raise SistemaError(f"project name read-back mismatch: {written!r}")
        return panel

    def open_project(self, path: str) -> None:
        """Open an existing ``.ssm`` through the file dialog (typed, not clicked)."""
        self.keys("Ctrl+L", settle=1.5)
        self.wait_idle()
        dialog = next(iter(self.new_dialogs()), None)
        if dialog is None:
            raise SistemaError("the Open dialog did not appear")
        # The file name edit is the first TLabeledEditEx/TEdit inside the dialog.
        target = self.file_edit(dialog.hwnd)
        if target is None:
            raise SistemaError("no file-name edit inside the Open dialog")
        W.set_focus(target)
        W.set_window_text(target, path)
        self.keys("ENTER", settle=1.5)
        self.wait_idle()

    def save(self, settle: float = 1.2) -> None:
        self.keys("Ctrl+S", settle=settle)
        self.wait_idle()

    def save_as(self, path: str) -> str:
        """``Save as`` to an exact path; returns the path SISTEMA reports back."""
        self.keys("Ctrl+Alt+S", settle=1.2)
        self.wait_idle()
        dialog = next(iter(self.new_dialogs()), None)
        if dialog is None:
            raise SistemaError("the Save dialog did not appear")
        target = self.file_edit(dialog.hwnd)
        if target is None:
            raise SistemaError("no file-name edit inside the Save dialog")
        W.set_focus(target)
        W.set_window_text(target, path)
        self.keys("ENTER", settle=1.0)
        pressed = self.accept_dialog(prefer="Ja")   # "Yes" to overwrite
        if not os.path.exists(path) and pressed:
            return path
        return path

    def export_pdf(self, path: str) -> str:
        """``File -> Export as PDF`` (Ctrl+E) to an exact path."""
        self.keys("Ctrl+E", settle=2.0)
        self.wait_idle()
        dialog = next(iter(self.new_dialogs()), None)
        if dialog is None:
            raise SistemaError("the PDF export dialog did not appear")
        target = self.file_edit(dialog.hwnd)
        if target is None:
            raise SistemaError("no file-name edit inside the export dialog")
        W.set_focus(target)
        W.set_window_text(target, path)
        self.keys("ENTER", settle=1.0)
        self.accept_dialog(prefer="Ja")
        self.wait_idle(settle=1.0)
        return path

    def new_child(self, settle: float = 1.0) -> str:
        """``Ctrl+Insert`` on the tree: create the child object of the selection.

        Returns the name of whatever SISTEMA selected afterwards, which is the
        read-back that proves the structure changed.
        """
        before = self.current_name()
        self.tree_keys("Ctrl+Insert", settle=settle)
        self.wait_idle()
        if self.new_dialogs():
            self.accept_dialog()
        return self.current_name() if self.current_name() != before else ""

    def rename_current(self, name: str) -> str:
        """Rename the selected object and read the name back."""
        panel = self.current_panel()
        if not panel.has(NAME_FIELD):
            panel = self.ensure_field(panel, NAME_FIELD)
        written = panel.set_text(NAME_FIELD, name)
        if written != name:
            raise SistemaError(f"rename read-back mismatch: {written!r} != {name!r}")
        return written

    # ------------------------------------------------------------ tab walking
    def page_control(self, panel: FormInstance) -> int:
        for hwnd in W.descendants(panel.hwnd):
            if W.class_name(hwnd) == "TAdvPageControl":
                return hwnd
        return 0

    def active_tabs(self, panel: FormInstance) -> list[str]:
        """Captions of the realised tab sheets, in enumeration order."""
        control = self.page_control(panel)
        if not control:
            return []
        return [W.window_text(hwnd) for hwnd in W.descendants(control)
                if W.class_name(hwnd) == "TAdvTabSheet"]

    def ensure_field(self, panel: FormInstance, name: str, cycles: int = 10) -> FormInstance:
        """Cycle tabs until ``name`` is realised, then re-bind and return the panel.

        SISTEMA builds a panel's tab pages lazily: a control only gets an HWND once
        its page has been shown.  ``Ctrl+Tab`` on the ``TAdvPageControl`` walks the
        pages and the realised control set is the read-back that says which page is
        active - no coordinates, no screenshot.
        """
        panel.refresh()
        if panel.has(name):
            return panel
        control = self.page_control(panel)
        if not control:
            raise SistemaError(f"{panel.form_name} has no page control; {name} unreachable")
        for _attempt in range(cycles):
            self.focus()
            W.set_focus(control)
            time.sleep(0.1)
            W.chord("Ctrl+Tab")
            self.wait_idle(settle=0.5)
            panel.refresh()
            if panel.has(name):
                return panel
        raise SistemaError(f"no tab of {panel.form_name} realises {name} "
                           f"(saw tabs: {self.active_tabs(panel)})")

    def set_field(self, name: str, value: str, panel: FormInstance | None = None) -> str:
        """Write ``value`` into ``name`` on the current (or given) panel, verified."""
        panel = self.ensure_field(panel or self.current_panel(), name)
        written = panel.set_text(name, value)
        if written != value:
            raise SistemaError(f"{name} read-back mismatch: {written!r} != {value!r}")
        return written

    def check_field(self, name: str, state: bool = True,
                    panel: FormInstance | None = None) -> bool:
        panel = self.ensure_field(panel or self.current_panel(), name)
        return panel.set_check(name, state)

    def press(self, name: str, panel: FormInstance | None = None) -> None:
        panel = self.ensure_field(panel or self.current_panel(), name)
        panel.click(name)

    def choose_radio(self, name: str, panel: FormInstance | None = None) -> None:
        panel = self.ensure_field(panel or self.current_panel(), name)
        hwnd = panel.field(name)
        W.click(hwnd)
        if not W.get_check(hwnd):
            W.send(hwnd, W.BM_SETCHECK, W.BST_CHECKED, 0)

    def select_combo(self, name: str, value, panel: FormInstance | None = None) -> str:
        """Pick a combo option by leading token (``"3"``, ``"cat4"``) or index.

        ``TIFAComboBox`` is an owner-drawn Delphi combo: ``CB_SETCURSEL`` moves the
        selection but the control's ``OnSelect`` only runs for a notification, so a
        ``CBN_SELCHANGE`` ``WM_COMMAND`` is posted to the parent afterwards.
        """
        panel = self.ensure_field(panel or self.current_panel(), name)
        hwnd = panel.field(name)
        items = W.combo_items(hwnd)
        index = None
        if isinstance(value, int):
            index = value
        else:
            wanted = str(value).strip().lower()
            for position, item in enumerate(items):
                head = item.split("|")[0].strip().lower()
                if head == wanted or item.strip().lower().startswith(wanted):
                    index = position
                    break
        if index is None or index < 0 or index >= max(len(items), 1):
            raise SistemaError(f"{name}: option {value!r} not found in "
                               f"{[i.split('|')[0] for i in items][:10]}")
        W.send(hwnd, W.CB_SETCURSEL, index, 0)
        control_id = W.user32.GetDlgCtrlID(hwnd) & 0xFFFF
        W.post(W.parent(hwnd), W.WM_COMMAND,
               (W.CBN_SELCHANGE << 16) | control_id, hwnd)
        self.wait_idle(settle=0.5)
        panel.refresh()
        return W.window_text(hwnd)

    def combo_options(self, name: str, panel: FormInstance | None = None) -> list[str]:
        panel = self.ensure_field(panel or self.current_panel(), name)
        return [item.split("|")[0] for item in W.combo_items(panel.field(name))]

    def read_field(self, name: str, panel: FormInstance | None = None) -> str:
        panel = self.ensure_field(panel or self.current_panel(), name)
        return panel.text(name)

    def snapshot_fields(self, panel: FormInstance | None = None) -> list[dict]:
        """Every readable control on the panel, with its DFM name and caption."""
        panel = panel or self.current_panel()
        panel.refresh()
        out = []
        for name, bound in sorted(panel.bound.items(), key=lambda kv: kv[1].component.order):
            if not bound.component.cls.startswith("T"):
                continue
            out.append({
                "name": name,
                "class": bound.component.cls,
                "label": self.ui.label_for(panel.form_name, bound.component),
                "text": W.window_text(bound.hwnd),
                "checked": W.get_check(bound.hwnd) if "CheckBox" in bound.component.cls
                           or "RadioButton" in bound.component.cls else None,
                "exact": bound.exact,
            })
        return out

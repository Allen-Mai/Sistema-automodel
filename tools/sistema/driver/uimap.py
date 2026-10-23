"""Address SISTEMA's controls by name, not by pixel.

The static UI map produced by ``tools/sistema/rea_ui_map.py`` knows every form,
every component, its DFM name, its parent container and its design-time
``Left``/``Top``.  At runtime Windows only tells us class names and rectangles.
:class:`FormInstance` joins the two:

1. estimate the form's DPI scale from its client size,
2. walk the live child-window tree, and for each window look for a DFM component
   with the same class under the matched parent whose scaled position is closest,
3. fall back to creation order for anything geometry cannot separate.

Every resolved control therefore gets a **DFM name** (``LEExName``,
``LEExB10D``, ``CB1_FncTypes``...), and ``FormInstance.field("LEExName")`` returns
its HWND directly - no coordinates, no screenshots.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field

from . import win32 as W

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_UI_MAP = os.path.join(os.path.dirname(HERE), "sistema_ui_map.json")

#: Container classes whose position/order cannot identify them (all pages share
#: the same rectangle and the Z order follows the active page).
SHEET_CLASSES = {"TAdvTabSheet", "TTabSheet"}


def set_dpi_aware() -> None:
    """Make this process DPI aware so window rectangles are physical pixels.

    Without it every coordinate is silently scaled by the virtualisation layer at
    150 % and geometry matching lands on the wrong control.
    """
    try:
        # PER_MONITOR_AWARE_V2
        if W.user32.SetProcessDpiAwarenessContext(ctypes_ptr(-4)):
            return
    except Exception:                                     # noqa: BLE001 - older Windows
        pass
    try:
        W.user32.SetProcessDPIAware()
    except Exception:                                     # noqa: BLE001
        pass


def ctypes_ptr(value: int):
    import ctypes
    return ctypes.c_void_p(value)


@dataclass
class Component:
    """One DFM component from the static map."""

    order: int
    cls: str
    name: str
    caption: str
    parent: str
    left: int
    top: int
    width: int
    height: int
    text: str | None = None
    label: str | None = None
    items: list[str] = field(default_factory=list)

    @property
    def right(self) -> int:
        return self.left + self.width

    @property
    def bottom(self) -> int:
        return self.top + self.height


class UiMap:
    """The static SISTEMA UI dictionary."""

    def __init__(self, path: str = DEFAULT_UI_MAP) -> None:
        with open(path, encoding="utf-8") as handle:
            document = json.load(handle)
        self.source: dict = document.get("source", {})
        self.forms: dict[str, dict] = document.get("forms", {})
        self.skipped: list[str] = document.get("skipped", [])
        # The PE resource name and the Delphi class name are not always the same
        # (``TFORMSSMMESSAGELISTUIABS`` resource, ``TFormSSMMessageListUI`` class),
        # so index both.
        self.by_class: dict[str, str] = {}
        for key, form in self.forms.items():
            self.by_class.setdefault(form.get("form", key).upper(), key)
        self._by_label: dict[str, list[dict]] = {}
        for form_name, form in self.forms.items():
            for label in form.get("labels", []):
                self._by_label.setdefault(label["caption"].lower(), []).append(
                    {**label, "form": form_name})

    # ---------------------------------------------------------------- queries
    def key_of(self, form_name: str) -> str:
        upper = form_name.upper()
        if upper in self.forms:
            return upper
        if upper in self.by_class:
            return self.by_class[upper]
        raise KeyError(f"form {form_name} is not in the UI map ({len(self.forms)} forms)")

    def form(self, form_name: str) -> dict:
        return self.forms[self.key_of(form_name)]

    def root_name(self, form_name: str) -> str:
        definition = self.form(form_name)
        return definition.get("name") or definition["form"]

    def components(self, form_name: str) -> list[Component]:
        definition = self.form(form_name)
        out = []
        for record in definition["components"]:
            if record["left"] is None:
                continue
            payload = {k: record[k] for k in
                       ("order", "cls", "name", "caption", "parent", "left", "top",
                        "width", "height", "text")}
            payload["label"] = record.get("label")
            payload["items"] = _find_items(definition, record["name"])
            out.append(Component(**payload))
        return out

    def find_label(self, needle: str) -> list[dict]:
        """Every label whose caption contains ``needle`` (case-insensitive)."""
        needle = needle.lower()
        hits = []
        for caption, entries in self._by_label.items():
            if needle in caption:
                hits.extend(entries)
        return sorted(hits, key=lambda e: (e["form"], e["order"]))

    def label_for(self, form_name: str, component: Component) -> str:
        """The caption the UI shows next to/above ``component``.

        ``TLabeledEditEx``-style controls paint their own caption, which the DFM
        stores in ``LabelCaption``; that is authoritative.  Plain edits fall back
        to the ``TLabel`` directly to their left on the same row.
        """
        if component.label:
            return component.label
        if component.caption:
            return component.caption
        best = None
        best_score = None
        for label in self.form(form_name)["labels"]:
            if label["kind"] != "TLabel" or label["top"] is None:
                continue
            dy = abs((label["top"] or 0) - component.top)
            if dy > 24:
                continue
            dx = component.left - (label["left"] or 0)
            if dx < 0 or dx > 400:
                continue
            score = dy * 1000 + dx
            if best_score is None or score < best_score:
                best, best_score = label, score
        return best["caption"] if best else ""


def _find_items(form: dict, name: str) -> list[str]:
    for key, value in form.get("combo_items", {}).items():
        if key == name:
            return list(value)
    return []


@dataclass
class Bound:
    """A DFM component matched to a live HWND."""

    component: Component
    hwnd: int
    exact: bool

    def __str__(self) -> str:                             # pragma: no cover
        return f"{self.component.name} -> {self.component.cls}#{self.hwnd:#x}"


class FormInstance:
    """A live panel form bound to its DFM definition."""

    def __init__(self, ui: UiMap, form_name: str, hwnd: int) -> None:
        self.ui = ui
        self.form_name = ui.key_of(form_name)
        self.definition = ui.form(self.form_name)
        self.hwnd = hwnd
        self.bound: dict[str, Bound] = {}
        self.unmatched: list[tuple[str, int]] = []
        self.scale = (1.0, 1.0)
        self.refresh()

    # ------------------------------------------------------------------ join
    def refresh(self) -> None:
        self.bound.clear()
        self.unmatched.clear()
        self.scale = self._estimate_scale()
        children: dict[str, list[Component]] = {}
        for comp in self.ui.components(self.form_name):
            children.setdefault(comp.parent, []).append(comp)
        self._match_tree(self.hwnd, self.ui.root_name(self.form_name), children)
        # Anything still unbound keeps a synthetic name so it stays addressable.
        seen = {bound.hwnd for bound in self.bound.values()}
        for hwnd in _immediate_children(self.hwnd):
            if hwnd not in seen:
                self.unmatched.append((f"@{W.class_name(hwnd)}#{hwnd & 0xFFFF:x}", hwnd))

    def _match_by_signature(self, live_hwnds: list[int], comps: list[Component],
                            children: dict[str, list[Component]]) -> None:
        """Pair container windows whose identity is their contents, not their box."""
        remaining = list(comps)
        for hwnd in live_hwnds:
            live_signature = _class_multiset(W.descendants(hwnd))
            best = None
            best_score = -1.0
            for comp in remaining:
                score = _similarity(live_signature,
                                    _dfm_multiset(children, comp.name))
                if score > best_score:
                    best, best_score = comp, score
            if best is None:
                continue
            remaining.remove(best)
            self.bound[best.name] = Bound(best, hwnd, best_score >= 0.6)
            self._match_tree(hwnd, best.name, children)

    def _estimate_scale(self) -> tuple[float, float]:
        """DPI scale, which is what VCL multiplies design-time coordinates by.

        The form's own client size is *not* usable: SISTEMA docks these panels and
        resizes them, so the ratio to the DFM ``ClientWidth`` is arbitrary.
        """
        dpi = 0
        try:
            dpi = int(W.user32.GetDpiForWindow(self.hwnd))
        except Exception:                                 # noqa: BLE001 - pre-1607
            dpi = 0
        if dpi <= 0:
            return (1.0, 1.0)
        factor = dpi / 96.0
        return (factor, factor)

    def _match_tree(self, parent_hwnd: int, parent_name: str,
                    children: dict[str, list[Component]]) -> None:
        candidates = list(children.get(parent_name, []))
        if not candidates:
            return
        origin_x, origin_y = _client_origin(parent_hwnd)
        live = _immediate_children(parent_hwnd)
        pool: dict[str, list[Component]] = {}
        for comp in candidates:
            pool.setdefault(comp.cls, []).append(comp)
        live_by_class: dict[str, list[int]] = {}
        for hwnd in live:
            live_by_class.setdefault(W.class_name(hwnd), []).append(hwnd)

        # Tab sheets all sit at (0,0) and Z-order rotates with the active page, so
        # neither geometry nor order identifies them: match by their subtree.
        for cls, hwnds in list(live_by_class.items()):
            if cls not in SHEET_CLASSES:
                continue
            self._match_by_signature(hwnds, pool.pop(cls, []), children)
            del live_by_class[cls]

        # Rows are separated by ``Top``; the horizontal offset between design and
        # runtime can drift by tens of pixels because ``TLabeledEditEx`` stretches
        # its own caption, so X is a weak signal and only aids tie-breaking.
        row_tolerance = 5
        column_tolerance = 80
        for cls, hwnds in live_by_class.items():
            comps = pool.get(cls)
            if not comps:
                continue
            remaining = sorted(comps, key=lambda c: c.order)
            matched: dict[int, Component] = {}
            exact: set[int] = set()
            # Pass 1 - geometry, with the row (``Top``) deciding and the column
            # only breaking ties.  The winner must be clearly better than the
            # runner-up, otherwise the row is ambiguous and pass 2 handles it.
            for hwnd in hwnds:
                x, y = _rel(hwnd, origin_x, origin_y)
                dy = y / self.scale[1]
                dx = x / self.scale[0]
                scored = sorted(
                    ((abs(comp.top - dy) * 100 + abs(comp.left - dx) / 10.0, comp)
                     for comp in remaining), key=lambda pair: pair[0])
                if not scored:
                    continue
                best_score, best = scored[0]
                if abs(best.top - dy) > row_tolerance or abs(best.left - dx) > column_tolerance:
                    continue
                runner_up = scored[1][0] if len(scored) > 1 else None
                if runner_up is not None and runner_up - best_score < 20:
                    continue
                matched[hwnd] = best
                exact.add(hwnd)
                remaining.remove(best)
            # Pass 2 - creation order for everything geometry could not separate.
            # Windows enumerates siblings from the top of the Z order, and VCL
            # puts each newly created child on top, so the live order is the
            # reverse of the DFM creation order.
            unbound = [hwnd for hwnd in hwnds if hwnd not in matched]
            for hwnd, comp in zip(unbound, reversed(remaining)):
                matched[hwnd] = comp
            for hwnd, comp in matched.items():
                self.bound[comp.name] = Bound(comp, hwnd, hwnd in exact)
                self._match_tree(hwnd, comp.name, children)

    # ---------------------------------------------------------------- access
    def field(self, name: str) -> int:
        """HWND of the DFM component called ``name``."""
        bound = self.bound.get(name)
        if bound is None:
            available = ", ".join(sorted(self.bound)[:12])
            raise KeyError(f"{self.form_name} has no component {name!r}; "
                           f"try one of: {available}")
        return bound.hwnd

    def has(self, name: str) -> bool:
        return name in self.bound

    def text(self, name: str) -> str:
        return W.window_text(self.field(name))

    def set_text(self, name: str, value: str, commit: bool = True) -> str:
        """Write a value, read it back, and - by default - commit it.

        ``WM_SETTEXT`` updates the edit control but SISTEMA stores the value in its
        own object model on ``OnExit``/``OnValueAccepted``, so focus is moved off
        the control afterwards.  Without that commit the panel shows the new text
        while the saved ``.ssm`` still holds the old one - a trap worth a test.
        """
        hwnd = self.field(name)
        W.replace_text(hwnd, value)
        if commit:
            # VCL raises OnExit when focus leaves the control; that is where
            # SISTEMA copies the text into its object model.
            W.set_focus(hwnd)
            W.press("TAB")
        return W.window_text(hwnd)

    def check(self, name: str) -> bool:
        return bool(W.get_check(self.field(name)))

    def set_check(self, name: str, state: bool) -> bool:
        hwnd = self.field(name)
        if bool(W.get_check(hwnd)) != state:
            W.click(hwnd)
        return bool(W.get_check(hwnd))

    def click(self, name: str) -> None:
        W.click(self.field(name))

    def items(self, name: str) -> list[str]:
        bound = self.bound.get(name)
        if bound is None:
            raise KeyError(f"{self.form_name} has no component {name!r}")
        live = W.combo_items(bound.hwnd)
        return live or list(bound.component.items)

    def fields(self) -> list[tuple[str, str, str]]:
        """``(dfm name, label caption, current text)`` for every readable control."""
        out = []
        for name, bound in sorted(self.bound.items(), key=lambda kv: kv[1].component.order):
            if not bound.component.cls.startswith("T"):
                continue
            label = self.ui.label_for(self.form_name, bound.component)
            out.append((name, label, W.window_text(bound.hwnd)))
        return out

    def describe(self) -> str:
        lines = [f"{self.form_name} hwnd={self.hwnd:#x} scale={self.scale[0]:.3f}x"
                 f"{self.scale[1]:.3f} bound={len(self.bound)}"]
        for name, bound in sorted(self.bound.items(), key=lambda kv: kv[1].component.order):
            mark = "" if bound.exact else "?"
            text = W.window_text(bound.hwnd)
            lines.append(f"  {mark:1s}{bound.component.order:4d} {bound.component.cls:24s} "
                         f"{name:28s} {text[:50]!r}")
        for name, hwnd in self.unmatched:
            lines.append(f"  !  {name:28s} {W.window_text(hwnd)[:50]!r}")
        return "\n".join(lines)


def _class_multiset(hwnds: list[int]):
    counts: dict[str, int] = {}
    for hwnd in hwnds:
        cls = W.class_name(hwnd)
        counts[cls] = counts.get(cls, 0) + 1
    return counts


def _dfm_multiset(children: dict[str, list[Component]], name: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    stack = [name]
    while stack:
        current = stack.pop()
        for child in children.get(current, []):
            counts[child.cls] = counts.get(child.cls, 0) + 1
            stack.append(child.name)
    return counts


def _similarity(left: dict[str, int], right: dict[str, int]) -> float:
    if not left or not right:
        return 0.0
    keys = set(left) | set(right)
    intersection = sum(min(left.get(key, 0), right.get(key, 0)) for key in keys)
    union = sum(max(left.get(key, 0), right.get(key, 0)) for key in keys)
    return intersection / union if union else 0.0


def _immediate_children(parent: int) -> list[int]:
    return [hwnd for hwnd in W.descendants(parent) if W.parent(hwnd) == parent]


def _client_origin(hwnd: int) -> tuple[int, int]:
    import ctypes
    from ctypes import wintypes as w
    point = w.POINT(0, 0)
    W.user32.ClientToScreen(w.HWND(hwnd), ctypes.byref(point))
    return (point.x, point.y)


def _rel(hwnd: int, origin_x: int, origin_y: int) -> tuple[int, int]:
    left, top, _right, _bottom = W.rect(hwnd)
    return (left - origin_x, top - origin_y)


def wait_for(predicate, timeout: float = 10.0, interval: float = 0.15):
    """Poll ``predicate`` until it returns something truthy."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        value = predicate()
        if value:
            return value
        time.sleep(interval)
    return None

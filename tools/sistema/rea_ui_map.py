"""Build a static UI map of SISTEMA from its embedded Delphi DFM resources - via REA.

Why this exists
---------------
SISTEMA has no UI Automation tree: the project tree, the Context panel and the
Messages panel are custom-drawn VCL controls, and the labels next to every input
box are ``TLabel`` objects that never create a window.  Screenshots used to be the
only way to tell which box was which, which is slow and fragile.

REA's ``inspect-pe-resources`` returns the complete PE resource inventory with
payload offsets and SHA-256 for every entry.  SISTEMA ships one ``RT_RCDATA``
binary DFM blob per form, so the inventory *is* the UI inventory: every form
class, every component name, every caption, every combo ``Items`` list, every
label text and its exact position.

Output (``sistema_ui_map.json``) is consumed by ``driver/attach.py``:

  * ``forms[<CLASS>].windows``       per-class components in DFM creation order,
    each with its exact parent, ``Left``/``Top`` and size.  Delphi creates child
    windows in DFM order and Windows enumerates them in creation/Z order, so the
    ordinal within a class is one join key; parent + geometry is the stronger one.
  * ``forms[<CLASS>].labels``        (caption, left, top) of every ``TLabel`` so a
    human or agent can name a field the way the UI does.
  * ``forms[<CLASS>].combo_items``   combo option lists (option text -> index).

Usage
-----
    python rea_ui_map.py                       # default: the installed SISTEMA.exe
    python rea_ui_map.py --exe <path> --out <dir>
    python rea_ui_map.py --no-rea              # fallback: enumerate resources via Win32
"""
from __future__ import annotations

import argparse
import ctypes
import json
import os
import re
import shutil
import subprocess
import sys
from ctypes import wintypes as w
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dfm  # noqa: E402

DEFAULT_EXE = r"C:\Program Files (x86)\SISTEMA 3.0.4\SISTEMA.exe"
RT_RCDATA = 10
FORM_NAME = re.compile(r"^T.*FORM.*$", re.IGNORECASE)

#: Forms an operator actually drives.  Third-party editor dialogs still get
#: parsed and stored, they are just left out of the Markdown summary.
CORE_FORMS = (
    "TFORMMAIN", "TFORMCOMPONENT", "TFORMCHANNEL", "TFORMCCFMEASURE",
    "TFORMCHANNELMANAGER", "TFORMCONFIG", "TFORMCONFIGCOMMON",
    "TFORMCONFIGCONTEXT", "TFORMCONFIGEXPERT", "TFORMCONFIGVIEW",
    "TFORMCONTEXT", "TFORMDCMEASUREDEVICE", "TFORMLIB",
    "TFORMLIBCCFMEASURES", "TFORMLIBDCMEASURES", "TFORMMESSAGELISTUI",
    "TFORMMESSAGEHELPERLISTUI", "TFORMNOP", "TFORMPROJECT", "TFORMREPORT12",
    "TFORMSF", "TFORMSPLASH", "TFORMSSMMESSAGELISTUIABS", "TFORMVERSIONDIFF",
    "TFORMINFOMESSAGE", "TFORMLOADFILE", "TFORMSETTINGS", "TFORMT10DDEVICELISTUI",
)


# --------------------------------------------------------------------- REA call
def find_rea() -> tuple[list[str], str] | None:
    """Return ``(argv_prefix, description)`` for the REA CLI, if installed."""
    for node_exe, script in _rea_candidates():
        if os.path.exists(node_exe) and os.path.exists(script):
            return [node_exe, script], f"{node_exe} {script}"
    exe = shutil.which("rea")
    if exe:
        return [exe], exe
    return None


def _rea_candidates():
    roots = [
        r"C:\Users\admin\AppData\Local\Programs\node24",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "node24"),
        os.path.join(os.environ.get("APPDATA", ""), "npm"),
        os.path.join(os.environ.get("ProgramFiles", ""), "nodejs"),
    ]
    for root in roots:
        if not root:
            continue
        yield (os.path.join(root, "node.exe"),
               os.path.join(root, "node_modules", "rea-agents", "scripts", "rea.mjs"))
        yield (os.path.join(root, "node.exe"),
               os.path.join(root, "npm", "node_modules", "rea-agents", "scripts", "rea.mjs"))


def rea_pe_resources(exe: str, workdir: str) -> dict:
    """Run ``rea inspect-pe-resources`` and return its ``normalized_result``."""
    found = find_rea()
    if not found:
        raise RuntimeError("REA CLI not found; run rea/install-rea.ps1 or pass --no-rea")
    argv, described = found
    cmd = argv + ["inspect-pe-resources", exe, "--format", "json"]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=900)
    if proc.returncode != 0:
        raise RuntimeError(f"rea inspect-pe-resources failed ({proc.returncode}): "
                           f"{(proc.stderr or proc.stdout)[:800]}")
    text = proc.stdout.strip()
    start = text.find("{")
    if start < 0:
        raise RuntimeError("rea produced no JSON document")
    document = json.loads(text[start:])
    result = document.get("normalized_result") or {}
    result["_rea"] = described
    with open(os.path.join(workdir, "rea-pe-resources.json"), "w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False)
    return result


# ------------------------------------------------------- fallback: Win32 resources
def win32_rcdtada(exe: str) -> list[dict]:
    """Enumerate ``RT_RCDATA`` entries with ``LoadLibraryEx`` + ``FindResource``.

    Used only when REA is unavailable; REA is preferred because it records the
    payload SHA-256 next to each entry.
    """
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    LOAD_LIBRARY_AS_DATAFILE = 0x00000002
    LPCWSTR = ctypes.c_wchar_p

    kernel32.LoadLibraryExW.restype = w.HMODULE
    kernel32.LoadLibraryExW.argtypes = [w.LPCWSTR, w.HANDLE, w.DWORD]
    kernel32.EnumResourceNamesW.restype = w.BOOL
    kernel32.EnumResourceNamesW.argtypes = [w.HMODULE, ctypes.c_void_p,
                                            ctypes.c_void_p, ctypes.c_void_p]
    kernel32.FindResourceW.restype = w.HANDLE
    kernel32.FindResourceW.argtypes = [w.HMODULE, ctypes.c_void_p, ctypes.c_void_p]
    kernel32.SizeofResource.restype = w.DWORD
    kernel32.SizeofResource.argtypes = [w.HMODULE, w.HANDLE]
    kernel32.LoadResource.restype = w.HANDLE
    kernel32.LoadResource.argtypes = [w.HMODULE, w.HANDLE]
    kernel32.LockResource.restype = ctypes.c_void_p
    kernel32.LockResource.argtypes = [w.HANDLE]
    kernel32.FreeLibrary.argtypes = [w.HMODULE]

    module = kernel32.LoadLibraryExW(exe, None, LOAD_LIBRARY_AS_DATAFILE)
    if not module:
        raise OSError(ctypes.get_last_error(), "LoadLibraryExW failed")
    collected: list[str] = []
    try:
        enum_proc = ctypes.WINFUNCTYPE(w.BOOL, w.HMODULE, ctypes.c_void_p,
                                       LPCWSTR, ctypes.c_void_p)

        def callback(_module, _type, name, _param):
            if name:
                collected.append(name)
            return True

        kernel32.EnumResourceNamesW(module, ctypes.c_void_p(RT_RCDATA),
                                    ctypes.cast(enum_proc(callback), ctypes.c_void_p), None)
        with open(exe, "rb") as handle:
            blob = handle.read()
        out: list[dict] = []
        for res_name in collected:
            info = kernel32.FindResourceW(module, LPCWSTR(res_name),
                                          ctypes.c_void_p(RT_RCDATA))
            if not info:
                continue
            size = kernel32.SizeofResource(module, info)
            handle = kernel32.LoadResource(module, info)
            if not handle:
                continue
            pointer = kernel32.LockResource(handle)
            payload = ctypes.string_at(pointer, size)
            out.append({"name": res_name, "size": size, "offset": blob.find(payload),
                        "payload": payload})
        return out
    finally:
        kernel32.FreeLibrary(module)


# ------------------------------------------------------------------- UI map build
def _labelled(node: dfm.Node) -> str | None:
    """The caption a control paints for itself (``TLabeledEditEx`` and friends)."""
    for key in ("LabelCaption", "Caption", "Text"):
        value = node.props.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def build_form(root: dfm.Node) -> dict:
    """Flatten one form into the lookups the runtime driver needs."""
    windows: dict[str, list[dict]] = {}
    labels: list[dict] = []
    items: dict[str, list[str]] = {}
    components: list[dict] = []
    parent_of: dict[int, str] = {}

    def visit(node: dfm.Node, parent: str) -> None:
        for child in node.children:
            parent_of[id(child)] = parent
            visit(child, child.name or child.cls)

    visit(root, root.name or root.cls)

    for order, node in enumerate(dfm.flatten(root)):
        if node is root:
            continue
        bounds = node.bounds
        record = {
            "order": order,
            "cls": node.cls,
            "name": node.name,
            "caption": node.caption,
            "left": bounds[0] if bounds else None,
            "top": bounds[1] if bounds else None,
            "width": bounds[2] if bounds else None,
            "height": bounds[3] if bounds else None,
            "parent": parent_of.get(id(node), ""),
            "tab_order": node.props.get("TabOrder"),
            "visible": node.props.get("Visible"),
            "label": _labelled(node),
            "label_second": node.props.get("LabelSecondCaption")
                            if isinstance(node.props.get("LabelSecondCaption"), str) else None,
            "read_only": node.props.get("ReadOnly"),
            "text": node.props.get("Text") if isinstance(node.props.get("Text"), str) else None,
        }
        components.append(record)
        if node.cls == "TLabel" or node.cls in {"TMenuItem", "TButton", "TBitBtn",
                                                "TIFABitBtn", "TToolButton"}:
            if node.caption:
                labels.append({"order": order, "caption": node.caption,
                               "left": record["left"], "top": record["top"],
                               "name": node.name, "kind": node.cls})
        item_list = node.items
        if item_list:
            items[node.name or f"{node.cls}#{order}"] = item_list
        if record["left"] is not None:
            windows.setdefault(node.cls, []).append(
                {"order": order, "name": node.name, "caption": record["caption"],
                 "label": record["label"], "text": record["text"],
                 "items": item_list, "parent": record["parent"],
                 "left": record["left"], "top": record["top"],
                 "width": record["width"], "height": record["height"],
                 "tab_order": record["tab_order"]})
    return {
        "form": root.cls,
        "name": root.name,
        "title": root.caption,
        "props": {k: v for k, v in root.props.items()
                  if isinstance(v, (str, int, bool)) and k in
                  {"Caption", "Name", "Width", "Height", "BorderStyle", "Position",
                   "ClientWidth", "ClientHeight"}},
        "windows": windows,
        "labels": labels,
        "combo_items": items,
        "components": components,
    }


def collect(exe: str, workdir: str, use_rea: bool) -> dict:
    if use_rea:
        resources = rea_pe_resources(exe, workdir)
        with open(exe, "rb") as handle:
            blob = handle.read()
        entries = []
        for entry in resources.get("resources", []):
            kind = entry.get("type") or {}
            if kind.get("id") != RT_RCDATA:
                continue
            name = entry.get("name") or {}
            if name.get("kind") != "name":
                continue
            payload = entry.get("payload") or {}
            location = payload.get("location") or {}
            if location.get("offset") is None or location.get("bytes") is None:
                continue
            entries.append({"name": name.get("name") or "",
                            "offset": location["offset"], "size": location["bytes"],
                            "sha256": payload.get("sha256")})
        source = {"mode": "rea", "cli": resources.get("_rea"),
                  "exe_sha256": (resources.get("artifact") or {}).get("sha256")}

        def payload_of(entry: dict) -> bytes:
            return blob[entry["offset"]:entry["offset"] + entry["size"]]
    else:
        raw = win32_rcdtada(exe)
        entries = [{"name": item["name"], "offset": item["offset"], "size": item["size"]}
                   for item in raw]
        fallback = {item["name"]: item["payload"] for item in raw}

        def payload_of(entry: dict) -> bytes:
            return fallback[entry["name"]]
        source = {"mode": "win32-fallback", "exe_sha256": None}

    forms: dict[str, dict] = {}
    skipped: list[str] = []
    for entry in entries:
        name = entry["name"]
        if not FORM_NAME.match(name):
            continue
        payload = payload_of(entry)
        if not payload.startswith(dfm.MAGIC):
            # RT_RCDATA also carries pngs, cursors and TMS resources; only blobs
            # starting with the TPF0 magic are forms.
            continue
        try:
            root = dfm.parse_resource(payload)
        except Exception as exc:                          # noqa: BLE001 - third-party blobs
            skipped.append(f"{name}: {exc}")
            continue
        forms[name.upper()] = build_form(root)

    return {
        "source": {
            **source,
            "exe": exe,
            "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "parser": "tools/sistema/dfm.py",
        },
        "forms": forms,
        "skipped": skipped,
    }


# ----------------------------------------------------------------------- reports
def _md_escape(text: str) -> str:
    return (text or "").replace("|", "\\|").replace("\r", " ").replace("\n", " / ")


def write_markdown(ui_map: dict, path: str) -> None:
    forms = ui_map["forms"]
    lines = [
        "# SISTEMA 静态 UI 地图（由 REA 提取）",
        "",
        f"- 可执行文件：`{ui_map['source']['exe']}`",
        f"- SHA-256：`{ui_map['source'].get('exe_sha256')}`",
        f"- 提取方式：{ui_map['source']['mode']}"
        + (f"（REA：`{ui_map['source'].get('cli')}`）" if ui_map["source"].get("cli") else ""),
        f"- 生成时间（UTC）：{ui_map['source']['generated_utc']}",
        f"- 解析成功的窗体：**{len(forms)}**",
        "",
        "本文件由 `tools/sistema/rea_ui_map.py` 自动生成，不要手工编辑。",
        "",
        "> 定位约定：Delphi 按 DFM 顺序创建子窗口，Windows 按创建顺序枚举子窗口；",
        "> 且 DFM 里每个控件都带父容器名与精确 Left/Top。",
        "> 因此运行时 hwnd 可以用「父容器 + 类名 + 坐标 + 同类序数」反查到 DFM 组件名，",
        "> 这是替代坐标点击、也替代截图判读的定位方式。",
        "",
    ]
    for name in sorted(forms):
        form = forms[name]
        if name not in CORE_FORMS:
            continue
        lines += [f"## {form['form']}", ""]
        if form["title"]:
            lines.append(f"标题：`{_md_escape(form['title'])}`")
            lines.append("")
        window_classes = ", ".join(
            f"`{cls}`×{len(entries)}" for cls, entries in sorted(form["windows"].items()))
        lines += [f"可寻址窗口类：{window_classes or '（无）'}", ""]
        if form["combo_items"]:
            lines.append("下拉框选项：")
            lines.append("")
            lines.append("| 组件 | 选项 |")
            lines.append("|---|---|")
            for comp, options in form["combo_items"].items():
                lines.append(f"| `{comp}` | {' ／ '.join(_md_escape(o) for o in options)} |")
            lines.append("")
        interesting = [c for c in form["components"]
                       if c["cls"] in {"TLabel", "TIFABitBtn", "TBitBtn", "TButton",
                                       "TAdvOfficeCheckBox", "THTMLCheckBox", "TRadioButton",
                                       "TIFAComboBox", "TLabeledEditEx", "TLabeledComboBoxEx",
                                       "TIFALabeledAdvEditEx", "TLabeledMemoEx", "TMenuItem"}]
        if interesting:
            lines.append("| 顺序 | 类 | DFM 名称 | 文本/标题 | 父容器 | 位置 |")
            lines.append("|---|---|---|---|---|---|")
            for comp in interesting[:500]:
                where = (f"{comp['left']},{comp['top']}"
                         if comp["left"] is not None else "")
                lines.append(f"| {comp['order']} | `{comp['cls']}` | `{comp['name']}` | "
                             f"{_md_escape(comp['caption'])[:90]} | `{comp['parent']}` | {where} |")
            lines.append("")
    leftovers = [n for n in sorted(forms) if n not in CORE_FORMS]
    if leftovers:
        lines += ["## 其它窗体（同样已解析入库）", "",
                  ", ".join(f"`{n}`" for n in leftovers), ""]
    if ui_map["skipped"]:
        lines += ["## 未能解析的资源", ""]
        lines += [f"- {_md_escape(item)}" for item in ui_map["skipped"]]
        lines.append("")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--exe", default=DEFAULT_EXE)
    parser.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                      "sistema_ui_map.json"))
    parser.add_argument("--workdir", default=None,
                        help="cache directory for raw REA output (default: next to --out)")
    parser.add_argument("--no-rea", action="store_true",
                        help="enumerate resources through Win32 instead of REA")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    if not os.path.exists(args.exe):
        print(f"SISTEMA.exe not found: {args.exe}", file=sys.stderr)
        return 2
    workdir = args.workdir or os.path.dirname(os.path.abspath(args.out))
    os.makedirs(workdir, exist_ok=True)
    ui_map = collect(args.exe, workdir, use_rea=not args.no_rea)
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(ui_map, handle, ensure_ascii=False, indent=1)
    md_path = os.path.splitext(args.out)[0] + ".md"
    write_markdown(ui_map, md_path)
    if not args.quiet:
        print(f"forms parsed : {len(ui_map['forms'])}")
        print(f"json         : {args.out}")
        print(f"markdown     : {md_path}")
        if ui_map["skipped"]:
            print(f"skipped      : {len(ui_map['skipped'])} resources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Thin, dependency-free Win32 layer for driving a Delphi/VCL application.

Everything the driver needs is here: window enumeration, cross-process text
read/write through window messages, button presses, checkbox state, real keyboard
input, clipboard access and foreground handling.

Two rules learned the hard way on SISTEMA and encoded below:

1. ``GetWindowText`` is **not** a state read.  For a window owned by another
   process it returns the cached title from the window station, which for a Delphi
   edit control can be stale or empty.  ``SendMessageW(hwnd, WM_GETTEXT)`` asks the
   control itself and is the only trustworthy read-back - use :func:`window_text`.
2. ``SetForegroundWindow`` is silently refused by the Windows foreground lock.
   :func:`focus_window` attaches to the current foreground thread's input queue
   first, which is what makes the refusal go away.
"""
from __future__ import annotations

import ctypes
import struct
import time
from ctypes import wintypes as w
from dataclasses import dataclass

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

# ------------------------------------------------------------------ constants
WM_SETTEXT = 0x000C
WM_GETTEXT = 0x000D
WM_GETTEXTLENGTH = 0x000E
WM_CLOSE = 0x0010
WM_COMMAND = 0x0111
WM_SYSCOMMAND = 0x0112
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_CHAR = 0x0102
WM_SYSKEYDOWN = 0x0104
WM_SYSKEYUP = 0x0105
WM_SETFOCUS = 0x0007
WM_KILLFOCUS = 0x0008
WM_GETDLGCODE = 0x0087
WM_USER = 0x0400

BM_GETCHECK = 0x00F0
BM_SETCHECK = 0x00F1
BM_CLICK = 0x00F5
BST_UNCHECKED = 0
BST_CHECKED = 1
BST_INDETERMINATE = 2

CB_GETCOUNT = 0x0146
CB_GETCURSEL = 0x0147
CB_SETCURSEL = 0x014E
CB_GETLBTEXT = 0x0148
CB_GETLBTEXTLEN = 0x0149

LB_GETCOUNT = 0x018B
LB_GETCURSEL = 0x0188
LB_SETCURSEL = 0x0186
LB_GETTEXT = 0x0189

EM_SETSEL = 0x00B1
EM_REPLACESEL = 0x00C2

SW_RESTORE = 9
SW_SHOW = 5
SWP_NOZORDER = 0x0004
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_SHOWWINDOW = 0x0040

GA_ROOT = 2
GA_PARENT = 1

VK = {
    "BACK": 0x08, "TAB": 0x09, "RETURN": 0x0D, "ENTER": 0x0D, "SHIFT": 0x10,
    "CONTROL": 0x11, "CTRL": 0x11, "MENU": 0x12, "ALT": 0x12, "PAUSE": 0x13,
    "CAPITAL": 0x14, "ESCAPE": 0x1B, "ESC": 0x1B, "SPACE": 0x20,
    "PRIOR": 0x21, "PAGEUP": 0x21, "NEXT": 0x22, "PAGEDOWN": 0x22,
    "END": 0x23, "HOME": 0x24, "LEFT": 0x25, "UP": 0x26, "RIGHT": 0x27,
    "DOWN": 0x28, "INSERT": 0x2D, "INS": 0x2D, "DELETE": 0x2E, "DEL": 0x2E,
    "LWIN": 0x5B, "RWIN": 0x5C, "APPS": 0x5D, "MULTIPLY": 0x6A, "ADD": 0x6B,
    "SUBTRACT": 0x6D, "DECIMAL": 0x6E, "DIVIDE": 0x6F,
    "F1": 0x70, "F2": 0x71, "F3": 0x72, "F4": 0x73, "F5": 0x74, "F6": 0x75,
    "F7": 0x76, "F8": 0x77, "F9": 0x78, "F10": 0x79, "F11": 0x7A, "F12": 0x7B,
    "NUMLOCK": 0x90, "SCROLL": 0x91,
}
for _c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":
    VK[_c] = ord(_c)

INPUT_KEYBOARD = 1
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004

# ------------------------------------------------------------------ prototypes
user32.EnumWindows.argtypes = [ctypes.c_void_p, w.LPARAM]
user32.EnumWindows.restype = w.BOOL
user32.EnumChildWindows.argtypes = [w.HWND, ctypes.c_void_p, w.LPARAM]
user32.EnumChildWindows.restype = w.BOOL
user32.GetClassNameW.argtypes = [w.HWND, w.LPWSTR, ctypes.c_int]
user32.GetClassNameW.restype = ctypes.c_int
user32.GetWindowTextLengthW.argtypes = [w.HWND]
user32.GetWindowTextLengthW.restype = ctypes.c_int
user32.SendMessageW.argtypes = [w.HWND, w.UINT, w.WPARAM, w.LPARAM]
user32.SendMessageW.restype = w.LPARAM
user32.SendMessageTimeoutW.argtypes = [w.HWND, w.UINT, w.WPARAM, w.LPARAM,
                                       w.UINT, w.UINT, ctypes.POINTER(ctypes.c_size_t)]
user32.SendMessageTimeoutW.restype = w.LPARAM
user32.PostMessageW.argtypes = [w.HWND, w.UINT, w.WPARAM, w.LPARAM]
user32.PostMessageW.restype = w.BOOL
user32.IsWindowVisible.argtypes = [w.HWND]
user32.IsWindowVisible.restype = w.BOOL
user32.IsWindowEnabled.argtypes = [w.HWND]
user32.IsWindowEnabled.restype = w.BOOL
user32.GetWindowRect.argtypes = [w.HWND, ctypes.POINTER(w.RECT)]
user32.GetWindowRect.restype = w.BOOL
user32.GetParent.argtypes = [w.HWND]
user32.GetParent.restype = w.HWND
user32.GetAncestor.argtypes = [w.HWND, w.UINT]
user32.GetAncestor.restype = w.HWND
user32.GetWindowThreadProcessId.argtypes = [w.HWND, ctypes.POINTER(w.DWORD)]
user32.GetWindowThreadProcessId.restype = w.DWORD
user32.GetForegroundWindow.restype = w.HWND
user32.SetForegroundWindow.argtypes = [w.HWND]
user32.SetForegroundWindow.restype = w.BOOL
user32.BringWindowToTop.argtypes = [w.HWND]
user32.BringWindowToTop.restype = w.BOOL
user32.ShowWindow.argtypes = [w.HWND, ctypes.c_int]
user32.ShowWindow.restype = w.BOOL
user32.SetWindowPos.argtypes = [w.HWND, w.HWND, ctypes.c_int, ctypes.c_int,
                                ctypes.c_int, ctypes.c_int, w.UINT]
user32.SetWindowPos.restype = w.BOOL
user32.AttachThreadInput.argtypes = [w.DWORD, w.DWORD, w.BOOL]
user32.AttachThreadInput.restype = w.BOOL
kernel32.GetCurrentThreadId.restype = w.DWORD
user32.SetFocus.argtypes = [w.HWND]
user32.SetFocus.restype = w.HWND
user32.GetFocus.restype = w.HWND
user32.GetGUIThreadInfo.argtypes = [w.DWORD, ctypes.c_void_p]
user32.GetGUIThreadInfo.restype = w.BOOL
user32.OpenClipboard.argtypes = [w.HWND]
user32.OpenClipboard.restype = w.BOOL
user32.CloseClipboard.restype = w.BOOL
user32.EmptyClipboard.restype = w.BOOL
user32.SetClipboardData.argtypes = [w.UINT, w.HANDLE]
user32.SetClipboardData.restype = w.HANDLE
user32.GetClipboardData.argtypes = [w.UINT]
user32.GetClipboardData.restype = w.HANDLE
user32.SendInput.argtypes = [w.UINT, ctypes.c_void_p, ctypes.c_int]
user32.SendInput.restype = w.UINT
user32.MapVirtualKeyW.argtypes = [w.UINT, w.UINT]
user32.MapVirtualKeyW.restype = w.UINT
user32.IsWindow.argtypes = [w.HWND]
user32.IsWindow.restype = w.BOOL
user32.GetDpiForWindow.argtypes = [w.HWND]
user32.GetDpiForWindow.restype = w.UINT
user32.GetDlgCtrlID.argtypes = [w.HWND]
user32.GetDlgCtrlID.restype = ctypes.c_int
CBN_SELCHANGE = 1
user32.PostThreadMessageW.argtypes = [w.DWORD, w.UINT, w.WPARAM, w.LPARAM]
user32.PostThreadMessageW.restype = w.BOOL

kernel32.GlobalAlloc.argtypes = [w.UINT, ctypes.c_size_t]
kernel32.GlobalAlloc.restype = w.HGLOBAL
kernel32.GlobalLock.argtypes = [w.HGLOBAL]
kernel32.GlobalLock.restype = ctypes.c_void_p
kernel32.GlobalUnlock.argtypes = [w.HGLOBAL]
kernel32.GlobalFree.argtypes = [w.HGLOBAL]
kernel32.GlobalFree.restype = w.HGLOBAL

CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002


class Win32Error(OSError):
    """A Win32 call failed; ``winerror`` carries the GetLastError code."""


@dataclass(frozen=True)
class Window:
    """One HWND with everything the driver needs to address it."""

    hwnd: int
    cls: str
    title: str
    rect: tuple[int, int, int, int]
    visible: bool
    enabled: bool
    pid: int = 0
    parent: int = 0
    depth: int = 0

    @property
    def width(self) -> int:
        return self.rect[2] - self.rect[0]

    @property
    def height(self) -> int:
        return self.rect[3] - self.rect[1]

    def __str__(self) -> str:                                # pragma: no cover
        return (f"{self.cls}#{self.hwnd:#x} {self.rect[0]},{self.rect[1]} "
                f"{self.width}x{self.height} {self.title[:60]!r}")


def _check(result, message: str) -> None:
    if not result:
        raise Win32Error(ctypes.get_last_error(), message)


# ------------------------------------------------------------------ enumeration
_ENUM = ctypes.WINFUNCTYPE(w.BOOL, w.HWND, w.LPARAM)


def _collect(enum_fn, root: int | None, limit: int) -> list[int]:
    found: list[int] = []

    def callback(hwnd, _param):
        found.append(hwnd)
        return len(found) < limit

    trampoline = _ENUM(callback)
    if root is None:
        enum_fn(trampoline, 0)
    else:
        enum_fn(root, trampoline, 0)
    return found


def top_windows(limit: int = 4000) -> list[int]:
    return _collect(user32.EnumWindows, None, limit)


def descendants(parent: int, limit: int = 20000) -> list[int]:
    """Every descendant of ``parent``.

    ``EnumChildWindows`` already walks the whole subtree; do **not** recurse into
    it or the count explodes (that mistake once produced 3.4M rows).
    """
    return _collect(user32.EnumChildWindows, parent, limit)


def class_name(hwnd: int) -> str:
    buffer = ctypes.create_unicode_buffer(256)
    length = user32.GetClassNameW(hwnd, buffer, 256)
    return buffer.value[:length] if length else ""


def window_text(hwnd: int, timeout_ms: int = 2000) -> str:
    """Ask the control for its text with ``WM_GETTEXT`` (never ``GetWindowText``).

    Returns ``""`` when the control does not answer within ``timeout_ms`` - which
    also covers a hung or modal-blocked UI instead of hanging the caller.
    """
    length = int(_send_timeout(hwnd, WM_GETTEXTLENGTH, 0, 0, timeout_ms) or 0)
    if length <= 0:
        return ""
    buffer = ctypes.create_unicode_buffer(length + 1)
    _send_timeout(hwnd, WM_GETTEXT, length + 1, ctypes.addressof(buffer), timeout_ms)
    return buffer.value


def _send_timeout(hwnd: int, msg: int, wparam: int, lparam: int, timeout_ms: int) -> int:
    result = ctypes.c_size_t(0)
    ok = user32.SendMessageTimeoutW(hwnd, msg, wparam, lparam, 0x0002,  # SMTO_ABORTIFHUNG
                                    timeout_ms, ctypes.byref(result))
    return int(result.value) if ok else 0


def send(hwnd: int, msg: int, wparam: int = 0, lparam: int = 0) -> int:
    return int(user32.SendMessageW(hwnd, msg, wparam, lparam))


def send_timeout(hwnd: int, msg: int, wparam: int = 0, lparam: int = 0,
                 timeout_ms: int = 2000) -> int:
    return _send_timeout(hwnd, msg, wparam, lparam, timeout_ms)


def post(hwnd: int, msg: int, wparam: int = 0, lparam: int = 0) -> bool:
    return bool(user32.PostMessageW(hwnd, msg, wparam, lparam))


def rect(hwnd: int) -> tuple[int, int, int, int]:
    area = w.RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(area)):
        return (0, 0, 0, 0)
    return (area.left, area.top, area.right, area.bottom)


def parent(hwnd: int) -> int:
    return int(user32.GetParent(hwnd) or 0)


def root(hwnd: int) -> int:
    return int(user32.GetAncestor(hwnd, GA_ROOT) or 0)


def pid_of(hwnd: int) -> int:
    value = w.DWORD(0)
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(value))
    return int(value.value)


def describe(hwnd: int) -> Window:
    return Window(
        hwnd=hwnd,
        cls=class_name(hwnd),
        title=window_text(hwnd),
        rect=rect(hwnd),
        visible=bool(user32.IsWindowVisible(hwnd)),
        enabled=bool(user32.IsWindowEnabled(hwnd)),
        pid=pid_of(hwnd),
        parent=parent(hwnd),
    )


def snapshot(pid: int | None = None, include_hidden: bool = False) -> list[Window]:
    """All top-level windows, optionally filtered to one process."""
    out = []
    for hwnd in top_windows():
        window = describe(hwnd)
        if pid is not None and window.pid != pid:
            continue
        if not include_hidden and not window.visible:
            continue
        out.append(window)
    return out


# ------------------------------------------------------------------ text writes
def set_window_text(hwnd: int, text: str, timeout_ms: int = 2000) -> bool:
    # The buffer must outlive the call: build it first and keep the reference.
    buffer = ctypes.create_unicode_buffer(text)
    ok = _send_timeout(hwnd, WM_SETTEXT, 0, ctypes.addressof(buffer), timeout_ms)
    return bool(ok)


def replace_text(hwnd: int, text: str) -> bool:
    """Set text the way a user would: select all, then ``EM_REPLACESEL``.

    Some Delphi controls ignore ``WM_SETTEXT`` for empty strings or keep stale
    edit state; going through the selection keeps the control's own undo/caret
    handling intact.
    """
    send(hwnd, EM_SETSEL, 0, -1)
    buffer = ctypes.create_unicode_buffer(text)
    send(hwnd, EM_REPLACESEL, 1, ctypes.addressof(buffer))
    if window_text(hwnd) != text:
        return set_window_text(hwnd, text)
    return True


def read_back(hwnd: int) -> str:
    return window_text(hwnd)


# ------------------------------------------------------------------ buttons
def click(hwnd: int) -> None:
    send(hwnd, BM_CLICK, 0, 0)


def get_check(hwnd: int) -> int:
    return send(hwnd, BM_GETCHECK, 0, 0)


def set_check(hwnd: int, state: int = BST_CHECKED) -> None:
    send(hwnd, BM_SETCHECK, state, 0)
    # VCL only fires OnClick from a real press for some subclasses.
    click(hwnd)


def combo_count(hwnd: int) -> int:
    return send(hwnd, CB_GETCOUNT, 0, 0)


def combo_items(hwnd: int) -> list[str]:
    items = []
    for index in range(combo_count(hwnd)):
        length = send(hwnd, CB_GETLBTEXTLEN, index, 0)
        if length <= 0:
            items.append("")
            continue
        buffer = ctypes.create_unicode_buffer(length + 1)
        send(hwnd, CB_GETLBTEXT, index, ctypes.addressof(buffer))
        items.append(buffer.value)
    return items


# ------------------------------------------------------------------ focus/keys
def focus_window(hwnd: int, settle: float = 0.05) -> bool:
    """Bring ``hwnd`` to the foreground, defeating the foreground lock."""
    current = int(user32.GetForegroundWindow() or 0)
    if current == hwnd:
        return True
    target_thread = user32.GetWindowThreadProcessId(hwnd, None)
    current_thread = int(kernel32.GetCurrentThreadId())
    foreground_thread = user32.GetWindowThreadProcessId(current, None) if current else 0
    attached_foreground = False
    attached_target = False
    if foreground_thread and foreground_thread != current_thread:
        attached_foreground = bool(user32.AttachThreadInput(current_thread,
                                                            foreground_thread, True))
    if target_thread and target_thread != current_thread:
        attached_target = bool(user32.AttachThreadInput(current_thread, target_thread, True))
    try:
        user32.ShowWindow(hwnd, SW_RESTORE)
        user32.BringWindowToTop(hwnd)
        user32.SetForegroundWindow(hwnd)
    finally:
        if attached_target:
            user32.AttachThreadInput(current_thread, target_thread, False)
        if attached_foreground:
            user32.AttachThreadInput(current_thread, foreground_thread, False)
    if settle:
        time.sleep(settle)
    return int(user32.GetForegroundWindow() or 0) == hwnd


def set_focus(control: int) -> bool:
    """Give keyboard focus to ``control`` across process boundaries."""
    thread = user32.GetWindowThreadProcessId(control, None)
    current_thread = int(kernel32.GetCurrentThreadId())
    attached = False
    if thread and thread != current_thread:
        attached = bool(user32.AttachThreadInput(current_thread, thread, True))
    try:
        user32.SetFocus(control)
    finally:
        if attached:
            user32.AttachThreadInput(current_thread, thread, False)
    return int(user32.GetFocus() or 0) == control


def _key_input(vk: int, up: bool, scan: int = 0, flags: int = 0) -> "KEYBDINPUT":
    return KEYBDINPUT(wVk=w.WORD(vk), wScan=w.WORD(scan), dwFlags=w.DWORD(flags), time=0,
                      dwExtraInfo=ctypes.c_size_t(0))


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", w.WORD), ("wScan", w.WORD), ("dwFlags", w.DWORD),
                ("time", w.DWORD), ("dwExtraInfo", ctypes.c_size_t)]


class _INPUTUNION(ctypes.Union):
    # MOUSEINPUT is the widest member (32 bytes on x64); keeping the union that
    # wide is what makes sizeof(INPUT) come out as the 40 bytes SendInput wants.
    _fields_ = [("ki", KEYBDINPUT), ("_pad", ctypes.c_uint64 * 4)]


class INPUT(ctypes.Structure):
    _anonymous_ = ("u",)
    _fields_ = [("type", w.DWORD), ("u", _INPUTUNION)]


def _send_inputs(events: list[INPUT]) -> None:
    if not events:
        return
    array = (INPUT * len(events))(*events)
    sent = user32.SendInput(len(events), array, ctypes.sizeof(INPUT))
    if sent != len(events):
        raise Win32Error(ctypes.get_last_error(),
                         f"SendInput sent {sent}/{len(events)} events")


def key_down(vk_name: str) -> None:
    vk = _vk(vk_name)
    _send_inputs([INPUT(type=INPUT_KEYBOARD,
                        u=_INPUTUNION(ki=_key_input(vk, False, _scan(vk))))])


def key_up(vk_name: str) -> None:
    vk = _vk(vk_name)
    _send_inputs([INPUT(type=INPUT_KEYBOARD,
                        u=_INPUTUNION(ki=_key_input(vk, True, _scan(vk),
                                                    KEYEVENTF_KEYUP)))])


def _scan(vk: int) -> int:
    return int(user32.MapVirtualKeyW(vk, 0))


def _vk(name: str) -> int:
    key = name.upper()
    if key not in VK:
        raise KeyError(f"unknown key {name!r}")
    return VK[key]


def press(vk_name: str, *modifiers: str, hold: float = 0.0) -> None:
    """Press ``vk_name`` with optional modifier keys held down."""
    for modifier in modifiers:
        key_down(modifier)
    try:
        key_down(vk_name)
        if hold:
            time.sleep(hold)
        key_up(vk_name)
    finally:
        for modifier in reversed(modifiers):
            key_up(modifier)


def chord(spec: str) -> None:
    """``"Ctrl+Alt+C"`` / ``"Ctrl+Insert"`` / ``"ENTER"`` style shortcut."""
    parts = [part.strip() for part in spec.split("+") if part.strip()]
    if not parts:
        return
    *modifiers, final = parts
    press(final, *modifiers)


def type_text(text: str) -> None:
    """Type arbitrary Unicode text through ``SendInput`` (no clipboard needed)."""
    events: list[INPUT] = []
    for char in text:
        for code, flags in ((ord(char), KEYEVENTF_UNICODE),
                            (ord(char), KEYEVENTF_UNICODE | KEYEVENTF_KEYUP)):
            events.append(INPUT(type=INPUT_KEYBOARD,
                                u=_INPUTUNION(ki=KEYBDINPUT(wVk=w.WORD(0), wScan=w.WORD(code),
                                                            dwFlags=w.DWORD(flags), time=0,
                                                            dwExtraInfo=ctypes.c_size_t(0)))))
    _send_inputs(events)


def key_message(hwnd: int, vk_name: str, modifiers: tuple[str, ...] = ()) -> None:
    """Post a key chord straight to a window, without touching real input state."""
    vk = _vk(vk_name)
    extended = 0x01000000 if vk in (VK["LEFT"], VK["RIGHT"], VK["UP"], VK["DOWN"],
                                    VK["HOME"], VK["END"], VK["PRIOR"], VK["NEXT"],
                                    VK["INSERT"], VK["DELETE"]) else 0
    for modifier in reversed(modifiers):
        post(hwnd, WM_KEYDOWN, _vk(modifier), 0)
    post(hwnd, WM_KEYDOWN, vk, extended)
    post(hwnd, WM_KEYUP, vk, extended | 0xC0000000)
    for modifier in modifiers:
        post(hwnd, WM_KEYUP, _vk(modifier), 0xC0000000)


# ------------------------------------------------------------------ clipboard
def clipboard_text() -> str:
    for _attempt in range(20):
        if user32.OpenClipboard(None):
            try:
                handle = user32.GetClipboardData(CF_UNICODETEXT)
                if not handle:
                    return ""
                pointer = kernel32.GlobalLock(handle)
                try:
                    return ctypes.wstring_at(pointer) if pointer else ""
                finally:
                    kernel32.GlobalUnlock(handle)
            finally:
                user32.CloseClipboard()
        time.sleep(0.02)
    raise Win32Error(0, "clipboard is busy")


def set_clipboard_text(text: str) -> None:
    payload = text.encode("utf-16-le") + b"\x00\x00"
    for _attempt in range(20):
        if not user32.OpenClipboard(None):
            time.sleep(0.02)
            continue
        try:
            user32.EmptyClipboard()
            handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(payload))
            if not handle:
                raise Win32Error(ctypes.get_last_error(), "GlobalAlloc failed")
            pointer = kernel32.GlobalLock(handle)
            ctypes.memmove(pointer, payload, len(payload))
            kernel32.GlobalUnlock(handle)
            user32.SetClipboardData(CF_UNICODETEXT, handle)
            return
        finally:
            user32.CloseClipboard()
    raise Win32Error(0, "clipboard is busy")


# ------------------------------------------------------------------ misc
def window_from_point(x: int, y: int) -> int:
    return int(user32.WindowFromPoint(w.POINT(x, y)) or 0)


user32.WindowFromPoint.argtypes = [w.POINT]
user32.WindowFromPoint.restype = w.HWND

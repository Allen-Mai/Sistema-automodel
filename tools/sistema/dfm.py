"""Delphi binary DFM (TPF0) parser.

SISTEMA.exe is a Delphi/VCL application, so **every form is embedded in the PE as
an ``RT_RCDATA`` resource in binary DFM form** (magic ``TPF0``).  Parsing those
resources gives us the complete UI inventory - form classes, component names,
captions, label texts, combo ``Items``, grid columns, menu captions - without
starting the program and without a single screenshot.

That inventory is what lets the automation address controls **by their printed
label** ("B10D", "nop", "Determine MTTFD value from B10D/B10") instead of by
pixel coordinates.

Binary object stream layout (Delphi ``Classes.pas``)::

    TPF0
    <object>*
    0x00                     end of sibling list

    object      := <prefix?> <ClassName:ShortString> <Name:ShortString>
                   <property>* 0x00 <object>* 0x00
    prefix      := 0xFn      (n = flags; bit0 ffInherited, bit1 ffChildPos, bit2 ffInline)
                              when bit1 is set an Int32 child position follows
    property    := <Name:ShortString> <value>
    value       := <TValueType:Byte> <payload>

ShortStrings are one length byte plus ANSI characters (cp1252 by default).
"""
from __future__ import annotations

import struct
from dataclasses import dataclass, field
from typing import Any

MAGIC = b"TPF0"

# TValueType order as emitted by TWriter.WriteValue
#: TValueType numbers, calibrated against the 182 DFM resources that ship inside
#: ``SISTEMA.exe`` (see ``rea_ui_map.py``).  Classic Delphi numbers are 0..18;
#: two of them differ in these streams, which is why the table is explicit here
#: instead of being inferred.
VA_NULL = 0
VA_LIST = 1
VA_INT8 = 2
VA_INT16 = 3
VA_INT32 = 4
VA_EXTENDED = 5
VA_STRING = 6
VA_IDENT = 7
VA_FALSE = 8
VA_TRUE = 9
VA_BINARY = 10
VA_SET = 11
VA_COLLECTION = 12
VA_SINGLE = 13
#: 14 is ``vaCurrency`` in classic enumerations, but SISTEMA's writer uses it for
#: collections introduced by ``vaList`` markers.  No currency property appears in
#: any of the shipped forms, so the collection reading wins.
VA_COLLECTION_ITEMS = 14
VA_DATE = 15
VA_WSTRING = 16
VA_INT64 = 17
VA_UTF8STRING = 18
VA_DOUBLE = 19
#: TValueType 20 behaves exactly like ``vaUTF8String`` (Int32 byte length + UTF-8
#: payload) and carries wide captions such as ``CCF-Maßnahme``.
VA_UTF8STRING_LONG = 20

FF_INHERITED, FF_CHILDPOS, FF_INLINE = 0x01, 0x02, 0x04


class DfmError(ValueError):
    pass


@dataclass
class Node:
    """One component (or collection item) in a DFM stream."""

    cls: str = ""
    name: str = ""
    props: dict[str, Any] = field(default_factory=dict)
    children: list["Node"] = field(default_factory=list)
    index: int = -1          # creation order, i.e. the Win32 Z-order/child order

    # ---- convenience views ------------------------------------------------
    @property
    def caption(self) -> str:
        """The text a user sees, whatever the component kind calls it."""
        for key in ("Caption", "Text", "Title", "Hint", "Data"):
            value = self.props.get(key)
            if isinstance(value, str) and value:
                return value
        return ""

    @property
    def items(self) -> list[str]:
        value = self.props.get("Items")
        return [v for v in value if isinstance(v, str)] if isinstance(value, list) else []

    @property
    def bounds(self) -> tuple[int, int, int, int] | None:
        try:
            left = int(self.props.get("Left", 0))
            top = int(self.props.get("Top", 0))
            width = int(self.props.get("Width", 0))
            height = int(self.props.get("Height", 0))
        except (TypeError, ValueError):
            return None
        return (left, top, width, height)

    def walk(self):
        yield self
        for child in self.children:
            yield from child.walk()


class _Cursor:
    __slots__ = ("data", "pos", "size")

    def __init__(self, data: bytes) -> None:
        self.data = data
        self.pos = 0
        self.size = len(data)

    def byte(self) -> int:
        if self.pos >= self.size:
            raise DfmError("unexpected end of DFM stream")
        value = self.data[self.pos]
        self.pos += 1
        return value

    def peek(self) -> int | None:
        return self.data[self.pos] if self.pos < self.size else None

    def take(self, count: int) -> bytes:
        if self.pos + count > self.size:
            raise DfmError("unexpected end of DFM stream")
        chunk = self.data[self.pos:self.pos + count]
        self.pos += count
        return chunk

    def skip(self, count: int) -> None:
        self.take(count)

    def short_string(self) -> str:
        length = self.byte()
        raw = self.take(length)
        return _decode_ansi(raw)

    def int32(self) -> int:
        return struct.unpack("<i", self.take(4))[0]


def _decode_ansi(raw: bytes) -> str:
    """DFM ShortStrings are ANSI; Delphi's default is the system code page."""
    for encoding in ("utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1", "replace")


def parse(data: bytes) -> Node:
    """Parse a ``TPF0`` blob and return the root node."""
    if not data.startswith(MAGIC):
        raise DfmError("not a binary DFM stream (missing TPF0 magic)")
    cursor = _Cursor(data)
    cursor.skip(len(MAGIC))
    root = _read_object(cursor, index=[0])
    if root is None:
        raise DfmError("empty DFM stream")
    return root


def parse_resource(payload: bytes) -> Node:
    """Parse one PE resource payload, tolerating a leading length prefix."""
    if payload.startswith(MAGIC):
        return parse(payload)
    # Some linkers emit the resource with a 4-byte size prefix.
    stripped = payload[4:] if len(payload) > 4 else payload
    if stripped.startswith(MAGIC):
        return parse(stripped)
    raise DfmError("payload does not contain a TPF0 stream")


def _read_object(cur: _Cursor, index: list[int]) -> Node | None:
    first = cur.byte()
    if first == 0:
        return None
    flags = 0
    if first & 0xF0 == 0xF0:
        flags = first & 0x0F
        if flags & FF_CHILDPOS:
            cur.skip(4)
        class_name = cur.short_string()
    else:
        # No prefix byte: the byte we consumed is the class-name length.
        cur.pos -= 1
        class_name = cur.short_string()
    node = Node(cls=class_name, index=index[0])
    index[0] += 1
    node.name = cur.short_string()
    _read_properties(cur, node)
    while cur.peek() not in (None, 0):
        child = _read_object(cur, index)
        if child is None:
            break
        node.children.append(child)
    if cur.peek() == 0:
        cur.skip(1)
    return node


def _read_properties(cur: _Cursor, node: Node) -> None:
    while True:
        if cur.peek() in (None, 0):
            if cur.peek() == 0:
                cur.skip(1)
            return
        name = cur.short_string()
        if not name:
            return
        try:
            node.props[name] = _read_value(cur)
        except DfmError:
            raise
        except Exception as exc:                      # noqa: BLE001 - hostile input
            raise DfmError(f"failed reading property {name!r} of {node.cls}") from exc


def _read_value(cur: _Cursor) -> Any:
    kind = cur.byte()
    if kind == VA_NULL:
        return None
    if kind == VA_LIST:
        values = []
        while cur.peek() != VA_NULL:
            values.append(_read_value(cur))
        cur.skip(1)
        return values
    if kind == VA_INT8:
        return struct.unpack("<b", cur.take(1))[0]
    if kind == VA_INT16:
        return struct.unpack("<h", cur.take(2))[0]
    if kind == VA_INT32:
        return cur.int32()
    if kind == VA_INT64:
        return struct.unpack("<q", cur.take(8))[0]
    if kind == VA_EXTENDED:
        return _decode_extended(cur.take(10))
    if kind == VA_SINGLE:
        return struct.unpack("<f", cur.take(4))[0]
    if kind == VA_DOUBLE:
        return struct.unpack("<d", cur.take(8))[0]
    if kind == VA_DATE:
        return struct.unpack("<d", cur.take(8))[0]
    if kind == VA_STRING:
        return _decode_ansi(cur.take(cur.byte()))
    if kind == VA_UTF8STRING:
        # Int32 length counted in UTF-16 code units, payload UTF-16LE.  The
        # length semantics are calibrated against every form in SISTEMA.exe: a
        # byte length here desynchronises the stream on the first non-ASCII
        # caption (``´`` written as ``01 00 00 00 b4 00``).
        length = cur.int32()
        return cur.take(length * 2).decode("utf-16-le", "replace")
    if kind == VA_UTF8STRING_LONG:
        # Int32 length counted in bytes, payload UTF-8.
        return cur.take(cur.int32()).decode("utf-8", "replace")
    if kind == VA_WSTRING:
        length = cur.int32()
        return cur.take(length * 2).decode("utf-16-le", "replace")
    if kind == VA_IDENT:
        return cur.short_string()
    if kind == VA_FALSE:
        return False
    if kind == VA_TRUE:
        return True
    if kind == VA_BINARY:
        size = cur.int32()
        return cur.take(size)
    if kind == VA_SET:
        members = []
        while cur.peek() not in (None, 0):
            members.append(cur.short_string())
        if cur.peek() == 0:
            cur.skip(1)
        return members
    if kind == VA_COLLECTION:
        items = []
        while True:
            marker = cur.byte()
            if marker == VA_NULL:
                break
            cur.pos -= 1
            item = Node(cls="Item", index=len(items))
            _read_properties(cur, item)
            items.append(item)
        return items
    if kind == VA_COLLECTION_ITEMS:
        # TValueType 14: repeated ``vaList``-introduced property lists closed by
        # ``vaNull``, then a final ``vaNull`` closes the collection.  An empty
        # collection is therefore a single ``0x00``.
        items = []
        while True:
            marker = cur.byte()
            if marker == VA_NULL:
                break
            if marker != VA_LIST:
                raise DfmError(f"collection item marked with TValueType {marker}")
            item = Node(cls="Item", index=len(items))
            _read_properties(cur, item)
            items.append(item)
        return items
    raise DfmError(f"unknown TValueType {kind}")


def _decode_extended(raw: bytes) -> float:
    """80-bit x87 extended -> Python float (DFM ``vaExtended``)."""
    mantissa = int.from_bytes(raw[0:8], "little")
    exponent = int.from_bytes(raw[8:10], "little") & 0x7FFF
    sign = -1.0 if raw[9] & 0x80 else 1.0
    if exponent == 0 and mantissa == 0:
        return 0.0 * sign
    return sign * mantissa * 2.0 ** (exponent - 16383 - 63)


# TValueType value 19 exists in newer Delphi releases for vaDouble.
VA_DOUBLE = 19


def flatten(root: Node) -> list[Node]:
    return list(root.walk())


def describe(root: Node, limit: int = 400) -> str:
    """Human readable subtree dump, used for diagnostics."""
    lines: list[str] = []

    def visit(node: Node, depth: int) -> None:
        if len(lines) >= limit:
            return
        label = node.caption.replace("\r", " ").replace("\n", " | ")[:90]
        bounds = node.bounds
        where = f" @{bounds[0]},{bounds[1]} {bounds[2]}x{bounds[3]}" if bounds else ""
        lines.append(f"{'  ' * depth}{node.cls} {node.name}{where}"
                     f"{(' : ' + label) if label else ''}")
        for child in node.children:
            visit(child, depth + 1)

    visit(root, 0)
    return "\n".join(lines)

"""End-to-end check: build a real project through the SISTEMA UI, then verify
the saved .ssm - without a single screenshot."""
import sys, os, time, json
BASE = r"C:\Users\admin\Desktop\DSH工作区\Sistema-automodel\tools\sistema"
sys.path.insert(0, BASE)
from driver.session import Sistema
from driver import win32 as W

OUT = r"C:\Users\admin\Desktop\DSH工作区\_setup\e2e"
os.makedirs(OUT, exist_ok=True)
TARGET = os.path.join(OUT, "DSH_AUTO.ssm")

s = Sistema().attach()
print("attached", s.pid)

# 1) name the current subsystem
cp = s.current_panel()
print("panel:", cp.form_name, "tabs:", s.active_tabs(cp))
print("rename SB ->", repr(s.rename_current("SB1 e-stop input")))

# 2) Category = 3 (read the option list first, then select and read back)
print("categories:", s.combo_options("CBCat"))
print("CBCat read-back:", repr(s.select_combo("CBCat", "3")))

# 3) save to an exact path
print("save as ->", s.save_as(TARGET))
time.sleep(2.0)
print("file exists:", os.path.exists(TARGET), "size:",
      os.path.getsize(TARGET) if os.path.exists(TARGET) else 0)

# 4) verify by re-reading the saved project
if os.path.exists(TARGET):
    import xml.etree.ElementTree as ET
    tree = ET.parse(TARGET)
    tables = {t.get("table_name"): t for t in tree.iter("table")}
    print("tables:", sorted(tables)[:20])
    for name in ("projectops", "sfops", "componentops", "channelops", "blocops"):
        table = tables.get(name)
        if table is None:
            print(f"  {name}: missing")
            continue
        rows = list(table.iter("row"))
        print(f"  {name}: {len(rows)} rows")
        for row in rows[:3]:
            attrs = dict(row.attrib)
            keep = {k: attrs.get(k) for k in
                    ("name", "cat", "channeltype", "mttfd", "dcavg", "ccfscore",
                     "plr", "plsubitemscal", "plcal", "pfhcal") if k in attrs}
            print("    ", keep)

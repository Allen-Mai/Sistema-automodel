import sys, os, json
BASE = r"C:\Users\admin\Desktop\DSH工作区\Sistema-automodel\tools\sistema"
sys.path.insert(0, BASE)
from driver.uimap import UiMap

ui = UiMap()
FORMS = sys.argv[1:] or ["TFormComponent", "TFormSF", "TFormCCFMeasure", "TFormProject"]
for name in FORMS:
    try:
        definition = ui.form(name)
    except KeyError as exc:
        print("!!", exc)
        continue
    print(f"\n######## {definition['form']}  ({definition.get('name')})  title={definition.get('title')!r}")
    comps = {c.name: c for c in ui.components(name)}
    for c in sorted(comps.values(), key=lambda c: c.order):
        if c.cls in ("TLabel", "TImage", "TBevel", "TImageList", "TAction", "TActionList",
                     "TPopupMenu", "TMenuItem", "TMainMenu", "TTimer", "TSplitter",
                     "TPaintBox", "TShape", "TStringList", "TColorDialog"):
            continue
        label = ui.label_for(definition["form"], c)
        extra = ""
        if c.items:
            extra = f" items={c.items[:6]}"
        print(f"  {c.order:4d} {c.cls:26s} {c.name:30s} {('«'+label+'»') if label else '':44s}"
              f" ({c.left},{c.top}){extra}")

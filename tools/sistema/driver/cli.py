"""Command line for driving a running SISTEMA without screenshots.

    python cli.py attach | launch | current | fields | tabs | tree
    python cli.py set <LEExName> <value>
    python cli.py check <CB1_FncTypes> on|off
    python cli.py combo <CBCat> <value>
    python cli.py new-project <name> | new-child | save | save-as <path>
    python cli.py export-pdf <path> | open <path> | dialogs
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from driver.session import Sistema, SistemaError  # noqa: E402


def _session(args) -> Sistema:
    if args.action == "launch":
        return Sistema().launch(args.path)
    return Sistema().attach()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("action", choices=[
        "attach", "launch", "current", "fields", "tabs", "tree", "set", "check",
        "combo", "new-project", "new-child", "save", "save-as", "export-pdf",
        "open", "dialogs", "rename"])
    parser.add_argument("values", nargs="*")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--path", default=None, help="project path for launch")
    args = parser.parse_args(argv)

    try:
        session = _session(args)
    except SistemaError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    action = args.action
    try:
        if action in ("attach", "launch"):
            print(json.dumps({"pid": session.pid, "main": session.main,
                              "tree": session.tree()}, indent=1))
        elif action == "current":
            panel = session.current_panel()
            payload = {"panel": panel.form_name, "name": session.current_name(),
                       "tabs": session.active_tabs(panel),
                       "fields": session.snapshot_fields(panel)}
            if args.json:
                print(json.dumps(payload, ensure_ascii=False, indent=1))
            else:
                print(f"panel={payload['panel']} name={payload['name']!r}")
                print(f"tabs={payload['tabs']}")
                for field in payload["fields"]:
                    print(f"  {field['name']:26s} {str(field['label'])[:38]:40s} "
                          f"{field['text'][:44]!r}")
        elif action == "fields":
            for field in session.snapshot_fields():
                print(json.dumps(field, ensure_ascii=False))
        elif action == "tabs":
            print(session.active_tabs(session.current_panel()))
        elif action == "tree":
            print({"tree": session.tree(), "panels": session.panel_hwnds()})
        elif action == "dialogs":
            print([{"cls": w.cls, "title": w.title, "rect": w.rect}
                   for w in session.dialogs()])
        elif action == "set":
            name, value = args.values[0], args.values[1]
            print(session.set_field(name, value))
        elif action == "rename":
            print(session.rename_current(args.values[0]))
        elif action == "check":
            print(session.check_field(args.values[0], args.values[1].lower() != "off"))
        elif action == "combo":
            print(session.select_combo(args.values[0], args.values[1]))
        elif action == "new-project":
            panel = session.new_project(args.values[0] if args.values else "")
            print(panel.text("LEExName"))
        elif action == "new-child":
            print(session.new_child() or session.current_panel().form_name)
        elif action == "save":
            session.save()
            print("saved")
        elif action == "save-as":
            print(session.save_as(args.values[0]))
        elif action == "export-pdf":
            print(session.export_pdf(args.values[0]))
        elif action == "open":
            session.open_project(args.values[0])
            print("opened")
    except SistemaError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

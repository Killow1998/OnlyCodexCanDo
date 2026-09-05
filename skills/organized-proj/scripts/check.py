#!/usr/bin/env python3
"""Read-only package/link checks; not a behavioral evaluation of the Skill."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-global", action="store_true", help="Validate source only; do not compare an installed copy.")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    errors = []
    text = (root / "SKILL.md").read_text(encoding="utf-8")
    if not re.match(r"\A---\r?\nname: organized-proj\r?\ndescription: .+\r?\n---\r?\n", text):
        errors.append("SKILL.md: expected name and nonempty description frontmatter")
    ui = (root / "agents/openai.yaml").read_text(encoding="utf-8")
    if 'display_name: "organizedProj"' not in ui or "$organized-proj" not in ui:
        errors.append("openai.yaml: expected display name and invocation")
    files = [p for p in root.rglob("*") if p.is_file()]
    for path in files:
        if path.suffix == ".pyc" or "__pycache__" in path.parts:
            errors.append(f"unexpected cache: {path.relative_to(root)}")
        if path.suffix != ".md":
            continue
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if re.match(r"[a-z]+://|#", target):
                continue
            if not (path.parent / target.split("#", 1)[0]).exists():
                errors.append(f"{path.relative_to(root)}: missing link {target}")
    if not args.skip_global:
        installed = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "skills" / root.name
        if installed.exists() and installed.resolve() != root:
            def contents(base):
                return {p.relative_to(base).as_posix(): p.read_bytes() for p in base.rglob("*") if p.is_file()}
            if contents(root) != contents(installed):
                errors.append("installed copy differs; deployment needs separate authorization")
        elif not installed.exists():
            print("[info] not installed globally")
    for error in errors:
        print(f"[fail] {error}")
    if not errors:
        print("[ok] package, links, and source hygiene; behavioral scenarios not executed")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

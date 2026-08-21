#!/usr/bin/env python3
"""Run release checks for the codex-home-audit skill."""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parents[1]
DEFAULT_GLOBAL_SKILL = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "skills" / SKILL_DIR.name
QUICK_VALIDATE = Path.home() / ".codex" / "skills" / ".system" / "skill-creator" / "scripts" / "quick_validate.py"


def run(name: str, args: list[str]) -> bool:
    print(f"[run] {name}")
    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    proc = subprocess.run(args, cwd=REPO_ROOT, env=env, check=False)
    if proc.returncode == 0:
        print(f"[ok] {name}")
        return True
    print(f"[fail] {name}: exit {proc.returncode}")
    return False


def iter_public_files(root: Path):
    for path in root.rglob("*"):
        if path.is_file() and path.suffix != ".pyc" and "__pycache__" not in path.parts:
            yield path


def content_check() -> bool:
    print("[run] content check")
    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    metadata = (SKILL_DIR / "agents" / "openai.yaml").read_text(encoding="utf-8")
    problems: list[str] = []
    for marker in ("[TODO:", "Structuring This Skill", "Replace with the first main section"):
        if marker in skill:
            problems.append(f"placeholder remains: {marker}")
    if len(skill.splitlines()) > 150:
        problems.append("SKILL.md exceeds 150 lines")
    if "references/cleanup-playbook.md" not in skill or "scripts/audit_codex_home.py" not in skill:
        problems.append("SKILL.md does not route both bundled resources")
    if "$codex-home-audit" not in metadata:
        problems.append("openai.yaml default prompt does not mention $codex-home-audit")
    if problems:
        print("[fail] content check")
        for problem in problems:
            print(f"  {problem}")
        return False
    print("[ok] content check")
    return True


def cache_check() -> bool:
    print("[run] cache check")
    caches = sorted(path for path in SKILL_DIR.rglob("__pycache__") if path.is_dir())
    if caches:
        print("[fail] cache check")
        for path in caches:
            print(f"  {path.relative_to(REPO_ROOT)}")
        return False
    print("[ok] cache check")
    return True


def digest(path: Path) -> str:
    # The installed copy is outside Git; digests detect stale or partial syncs.
    value = hashlib.sha256()
    value.update(path.read_bytes())
    return value.hexdigest()


def manifest(root: Path) -> dict[str, str]:
    return {str(path.relative_to(root)): digest(path) for path in iter_public_files(root)}


def global_consistency(target: Path) -> bool:
    print("[run] global skill consistency")
    if not target.exists():
        print(f"[warn] global skill missing: {target}")
        return True
    source = manifest(SKILL_DIR)
    installed = manifest(target)
    if source == installed:
        print("[ok] global skill consistency")
        return True
    print("[fail] global skill consistency")
    for label, values in (
        ("missing", sorted(set(source) - set(installed))),
        ("extra", sorted(set(installed) - set(source))),
        ("changed", sorted(key for key in set(source) & set(installed) if source[key] != installed[key])),
    ):
        if values:
            print(f"  {label}: {', '.join(values[:20])}")
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--global-skill", default=str(DEFAULT_GLOBAL_SKILL))
    parser.add_argument("--skip-global", action="store_true")
    args = parser.parse_args()

    python = sys.executable
    syntax_code = "import pathlib, sys; [compile(pathlib.Path(p).read_text(encoding='utf-8'), p, 'exec') for p in sys.argv[1:]]"
    checks = [
        content_check(),
        cache_check(),
        run("unit tests", [python, "-B", "-m", "unittest", "discover", "-s", str(SKILL_DIR / "tests")]),
        run("syntax check", [python, "-B", "-c", syntax_code, str(SKILL_DIR / "scripts" / "audit_codex_home.py"), str(SKILL_DIR / "scripts" / "check.py")]),
    ]
    if QUICK_VALIDATE.exists():
        checks.append(run("skill validate", [python, "-B", str(QUICK_VALIDATE), str(SKILL_DIR.relative_to(REPO_ROOT))]))
    else:
        print(f"[warn] skill validate skipped; not found: {QUICK_VALIDATE}")
    if not args.skip_global:
        checks.append(global_consistency(Path(args.global_skill).expanduser()))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())

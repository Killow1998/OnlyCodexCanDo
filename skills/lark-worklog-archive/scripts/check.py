#!/usr/bin/env python3
"""Run release checks for the lark-worklog-archive skill."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parents[1]
DEFAULT_GLOBAL_SKILL = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "skills" / SKILL_DIR.name
QUICK_VALIDATE = Path.home() / ".codex" / "skills" / ".system" / "skill-creator" / "scripts" / "quick_validate.py"
EXCLUDED_NAMES = {"__pycache__", "monthly-docs.local.json"}
FORBIDDEN_PATTERNS = [
    re.compile(r"https?://(?:[a-z0-9-]+\.)*(?:feishu\.cn|larksuite\.com)(?=[:/]|$)\S*", re.IGNORECASE),
    re.compile(r"\bou_[0-9a-zA-Z_-]{16,}\b"),
    re.compile(r"\bcli_[a-zA-Z0-9_-]{12,}\b"),
]


def run(name: str, args: list[str]) -> bool:
    print(f"[run] {name}")
    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    proc = subprocess.run(args, cwd=REPO_ROOT, env=env, text=True, encoding="utf-8", errors="replace", check=False)
    if proc.returncode == 0:
        print(f"[ok] {name}")
        return True
    print(f"[fail] {name}: exit {proc.returncode}")
    return False


def iter_public_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in EXCLUDED_NAMES for part in relative.parts):
            continue
        if path.suffix == ".pyc":
            continue
        yield path


def sensitive_scan() -> bool:
    print("[run] sensitive scan")
    paths = sorted(REPO_ROOT.glob("README*.md"))
    paths.append(REPO_ROOT / ".gitignore")
    paths.extend(iter_public_files(SKILL_DIR))
    violations: list[str] = []
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(text):
                violations.append(str(path.relative_to(REPO_ROOT)))
                break
    if violations:
        print("[fail] sensitive scan")
        for item in sorted(set(violations)):
            print(f"  {item}")
        return False
    print("[ok] sensitive scan")
    return True


def cache_dir_scan() -> bool:
    print("[run] cache directory scan")
    caches = sorted(path for path in SKILL_DIR.rglob("__pycache__") if path.is_dir())
    if caches:
        print("[fail] cache directory scan")
        for path in caches:
            print(f"  {path.relative_to(REPO_ROOT)}")
        return False
    print("[ok] cache directory scan")
    return True


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def manifest(root: Path) -> dict[str, str]:
    return {str(path.relative_to(root)): file_hash(path) for path in iter_public_files(root)}


def global_consistency(target: Path) -> bool:
    print("[run] global skill consistency")
    if not target.exists():
        print(f"[warn] global skill missing: {target}")
        return True
    source_manifest = manifest(SKILL_DIR)
    target_manifest = manifest(target)
    missing = sorted(set(source_manifest) - set(target_manifest))
    extra = sorted(set(target_manifest) - set(source_manifest))
    changed = sorted(path for path in set(source_manifest) & set(target_manifest) if source_manifest[path] != target_manifest[path])
    if missing or extra or changed:
        print("[fail] global skill consistency")
        for label, values in (("missing", missing), ("extra", extra), ("changed", changed)):
            if values:
                print(f"  {label}:")
                for value in values[:20]:
                    print(f"    {value}")
                if len(values) > 20:
                    print(f"    ... {len(values) - 20} more")
        return False
    print("[ok] global skill consistency")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--global-skill", default=str(DEFAULT_GLOBAL_SKILL), help="Installed global skill path to compare when present.")
    parser.add_argument("--skip-global", action="store_true", help="Skip comparing the global installed skill copy.")
    args = parser.parse_args()

    python = sys.executable
    syntax_code = "import pathlib, sys; [compile(pathlib.Path(p).read_text(encoding='utf-8'), p, 'exec') for p in sys.argv[1:]]"
    checks = [
        run("unit tests", [python, "-B", "-m", "unittest", "discover", "-s", str(SKILL_DIR / "tests")]),
        run("syntax check", [python, "-B", "-c", syntax_code, str(SKILL_DIR / "scripts" / "archive_worklog.py"), str(SKILL_DIR / "scripts" / "install.py"), str(SKILL_DIR / "scripts" / "check.py")]),
        sensitive_scan(),
        cache_dir_scan(),
        run("install dry-run", [python, "-B", str(SKILL_DIR / "scripts" / "install.py"), "--dry-run"]),
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

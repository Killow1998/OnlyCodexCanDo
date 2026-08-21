#!/usr/bin/env python3
"""Measure Codex home file counts and sizes without reading file contents."""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
from pathlib import Path
from typing import Any


IDENTIFIER_RE = re.compile(
    r"^(?:[0-9a-fA-F]{8}-[0-9a-fA-F-]{27,}|[0-9a-fA-F]{24,}|[A-Za-z0-9_-]{32,})$"
)
DB_ENDINGS = (".db", ".sqlite", ".sqlite3", ".db-wal", ".db-shm", ".sqlite-wal", ".sqlite-shm")


def default_codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    return Path(configured).expanduser() if configured else Path.home() / ".codex"


def safe_bucket(name: str, is_dir: bool) -> str:
    if len(name) > 64 or IDENTIFIER_RE.fullmatch(name):
        return "<other-directories>" if is_dir else "<other-files>"
    return name


def stat_is_reparse(item_stat: os.stat_result) -> bool:
    attributes = getattr(item_stat, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return bool(reparse_flag and attributes & reparse_flag)


def is_reparse_or_link(entry: os.DirEntry[str], item_stat: os.stat_result) -> bool:
    if entry.is_symlink():
        return True
    return stat_is_reparse(item_stat)


def is_database_like(name: str) -> bool:
    return name.lower().endswith(DB_ENDINGS)


def new_category() -> dict[str, int]:
    return {"files": 0, "directories": 0, "bytes": 0, "links_skipped": 0}


def count_worktree_roots(root: Path) -> int:
    worktrees = root / "worktrees"
    try:
        worktrees_stat = worktrees.lstat()
        if stat.S_ISLNK(worktrees_stat.st_mode) or stat_is_reparse(worktrees_stat) or not stat.S_ISDIR(worktrees_stat.st_mode):
            return 0
        count = 0
        with os.scandir(worktrees) as entries:
            for entry in entries:
                try:
                    item_stat = entry.stat(follow_symlinks=False)
                    if is_reparse_or_link(entry, item_stat):
                        continue
                    if stat.S_ISDIR(item_stat.st_mode):
                        count += 1
                except OSError:
                    continue
        return count
    except OSError:
        return 0


def scan_codex_home(root: Path, max_entries: int = 1_000_000) -> dict[str, Any]:
    root = root.expanduser().resolve(strict=False)
    if not root.exists():
        raise FileNotFoundError(f"Codex home does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Codex home is not a directory: {root}")

    result: dict[str, Any] = {
        "codex_home": str(root),
        "files": 0,
        "directories": 0,
        "bytes": 0,
        "links_skipped": 0,
        "errors": 0,
        "entries_scanned": 0,
        "truncated": False,
        "database_like": {"files": 0, "bytes": 0},
        "worktree_roots": count_worktree_roots(root),
        "categories": {},
    }
    categories: dict[str, dict[str, int]] = result["categories"]
    stack: list[tuple[Path, str | None]] = [(root, None)]

    while stack and not result["truncated"]:
        current, inherited_bucket = stack.pop()
        try:
            with os.scandir(current) as entries:
                for entry in entries:
                    if max_entries and result["entries_scanned"] >= max_entries:
                        result["truncated"] = True
                        break
                    result["entries_scanned"] += 1
                    try:
                        item_stat = entry.stat(follow_symlinks=False)
                    except OSError:
                        result["errors"] += 1
                        continue

                    link_like = is_reparse_or_link(entry, item_stat)
                    is_dir = stat.S_ISDIR(item_stat.st_mode) and not link_like
                    bucket = inherited_bucket or safe_bucket(entry.name, is_dir)
                    category = categories.setdefault(bucket, new_category())

                    if link_like:
                        result["links_skipped"] += 1
                        category["links_skipped"] += 1
                    elif is_dir:
                        result["directories"] += 1
                        category["directories"] += 1
                        stack.append((Path(entry.path), bucket))
                    elif stat.S_ISREG(item_stat.st_mode):
                        size = max(0, item_stat.st_size)
                        result["files"] += 1
                        result["bytes"] += size
                        category["files"] += 1
                        category["bytes"] += size
                        if is_database_like(entry.name):
                            result["database_like"]["files"] += 1
                            result["database_like"]["bytes"] += size
        except OSError:
            result["errors"] += 1

    return result


def human_bytes(value: int) -> str:
    units = ("B", "KiB", "MiB", "GiB", "TiB")
    size = float(value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    raise AssertionError("unreachable")


def render_table(result: dict[str, Any], top: int) -> str:
    lines = [
        f"Codex home: {result['codex_home']}",
        f"Total: {human_bytes(result['bytes'])}, {result['files']} files, {result['directories']} directories",
        f"Scan: {result['entries_scanned']} entries, {result['links_skipped']} links/junctions skipped, "
        f"{result['errors']} errors, truncated={str(result['truncated']).lower()}",
        f"Database-like files: {result['database_like']['files']} totaling {human_bytes(result['database_like']['bytes'])}",
        f"Immediate worktree directories: {result['worktree_roots']}",
        "",
        "Top-level category                 Size        Files       Dirs  Links",
        "--------------------------------------------------------------------",
    ]
    ordered = sorted(result["categories"].items(), key=lambda item: (item[1]["bytes"], item[1]["files"]), reverse=True)
    for name, values in ordered[:top]:
        display = name if len(name) <= 32 else name[:29] + "..."
        lines.append(
            f"{display:<32} {human_bytes(values['bytes']):>10} {values['files']:>10} "
            f"{values['directories']:>10} {values['links_skipped']:>6}"
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-home", type=Path, default=default_codex_home())
    parser.add_argument("--format", choices=("table", "json"), default="table")
    parser.add_argument("--top", type=int, default=20, help="Maximum top-level categories in table output.")
    parser.add_argument("--max-entries", type=int, default=1_000_000, help="Stop after this many entries; 0 disables the cap.")
    args = parser.parse_args()
    if args.top < 1:
        parser.error("--top must be at least 1")
    if args.max_entries < 0:
        parser.error("--max-entries cannot be negative")

    try:
        result = scan_codex_home(args.codex_home, args.max_entries)
    except (FileNotFoundError, NotADirectoryError) as exc:
        parser.exit(2, f"error: {exc}\n")
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(render_table(result, args.top))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

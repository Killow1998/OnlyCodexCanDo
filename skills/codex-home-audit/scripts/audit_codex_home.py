#!/usr/bin/env python3
"""Measure Codex home growth and storage without exposing private state."""

from __future__ import annotations

import argparse
import heapq
import json
import os
import re
import stat
from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import Any, Callable


IDENTIFIER_RE = re.compile(
    r"^(?:[0-9a-fA-F]{8}-[0-9a-fA-F-]{27,}|[0-9a-fA-F]{24,}|[A-Za-z0-9_-]{32,})$"
)
DB_ENDINGS = (".db", ".sqlite", ".sqlite3", ".db-wal", ".db-shm", ".sqlite-wal", ".sqlite-shm")
ERROR_KINDS = ("stat", "scandir", "worktree", "session_read", "session_json")
SESSION_BUCKETS = {"sessions", "archived_sessions"}
COMPACTION_TYPES = {"compacted", "compaction", "context_compacted"}
TOOL_OUTPUT_TYPES = {"function_call_output", "custom_tool_call_output", "tool_output", "tool_result"}


def default_codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    return Path(configured).expanduser() if configured else Path.home() / ".codex"


def parse_since(value: str) -> datetime:
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected YYYY-MM-DD") from exc
    return datetime.combine(parsed, time.min, tzinfo=timezone.utc)


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


def new_file_totals() -> dict[str, Any]:
    return {
        "files": 0,
        "bytes": 0,
        "unique_bytes": 0,
        "allocated_bytes": 0,
        "hardlink_duplicates": 0,
        "_allocation_complete": True,
    }


def new_category() -> dict[str, Any]:
    return {**new_file_totals(), "directories": 0, "links_skipped": 0}


def file_identity(item_stat: os.stat_result) -> tuple[int, int] | None:
    inode = getattr(item_stat, "st_ino", 0)
    if not inode:
        return None
    return int(getattr(item_stat, "st_dev", 0)), int(inode)


def allocated_file_bytes(item_stat: os.stat_result) -> int | None:
    blocks = getattr(item_stat, "st_blocks", None)
    if blocks is None:
        return None
    return max(0, int(blocks) * 512)


def add_file(
    totals: dict[str, Any],
    size: int,
    allocated: int | None,
    identity: tuple[int, int] | None,
    seen: set[tuple[int, int]],
) -> None:
    totals["files"] += 1
    totals["bytes"] += size
    if identity is not None and identity in seen:
        totals["hardlink_duplicates"] += 1
        return
    if identity is not None:
        seen.add(identity)
    totals["unique_bytes"] += size
    if allocated is None:
        totals["_allocation_complete"] = False
    else:
        totals["allocated_bytes"] += allocated


def finalize_totals(totals: dict[str, Any]) -> None:
    if not totals.pop("_allocation_complete"):
        totals["allocated_bytes"] = None


def count_worktree_roots(root: Path) -> tuple[int, int]:
    worktrees = root / "worktrees"
    try:
        worktrees_stat = worktrees.lstat()
    except FileNotFoundError:
        return 0, 0
    except OSError:
        return 0, 1
    if stat.S_ISLNK(worktrees_stat.st_mode) or stat_is_reparse(worktrees_stat) or not stat.S_ISDIR(worktrees_stat.st_mode):
        return 0, 0

    count = 0
    errors = 0
    try:
        with os.scandir(worktrees) as entries:
            for entry in entries:
                try:
                    item_stat = entry.stat(follow_symlinks=False)
                    if is_reparse_or_link(entry, item_stat):
                        continue
                    if stat.S_ISDIR(item_stat.st_mode):
                        count += 1
                except OSError:
                    errors += 1
    except OSError:
        errors += 1
    return count, errors


def collect_type_markers(value: Any, markers: set[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "type" and isinstance(child, str):
                markers.add(child.lower())
            else:
                collect_type_markers(child, markers)
    elif isinstance(value, list):
        for child in value:
            collect_type_markers(child, markers)


def classify_session_record(value: Any) -> tuple[str, bool, bool, bool]:
    if not isinstance(value, dict):
        return "other", False, False, False
    markers: set[str] = set()
    collect_type_markers(value, markers)
    envelope_type = str(value.get("type", "")).lower()
    payload = value.get("payload")
    payload_type = str(payload.get("type", "")).lower() if isinstance(payload, dict) else ""
    is_compaction = bool(markers & COMPACTION_TYPES)
    is_tool_output = bool(markers & TOOL_OUTPUT_TYPES)
    is_image = any("image" in marker or "screenshot" in marker for marker in markers)

    if is_compaction:
        category = "compaction"
    elif is_tool_output:
        category = "tool_output"
    elif is_image:
        category = "image"
    elif envelope_type in {"session_meta", "turn_context", "event_msg", "response_item"}:
        category = envelope_type
    elif payload_type in {"session_meta", "turn_context", "event_msg", "response_item"}:
        category = payload_type
    else:
        category = "other"
    return category, is_compaction, is_tool_output, is_image


def utc_timestamp(value: float) -> str:
    return datetime.fromtimestamp(value, timezone.utc).isoformat().replace("+00:00", "Z")


def analyze_session_candidates(
    candidates: list[tuple[int, str, float]],
    record_error: Callable[[str], None],
) -> dict[str, Any]:
    ordered = sorted(candidates, key=lambda item: (item[0], item[1]), reverse=True)
    summary: dict[str, Any] = {
        "sampled_files": len(ordered),
        "records": 0,
        "bytes_read": 0,
        "category_counts": {},
        "category_bytes": {},
        "compaction_records": 0,
        "compaction_bytes": 0,
        "tool_output_records": 0,
        "tool_output_bytes": 0,
        "image_records": 0,
        "image_bytes": 0,
        "largest_files": [],
    }

    for rank, (size, path_text, modified) in enumerate(ordered, start=1):
        summary["largest_files"].append(
            {"rank": rank, "size": size, "mtime_utc": utc_timestamp(modified)}
        )
        try:
            with open(path_text, "rb") as stream:
                for raw_line in stream:
                    line_bytes = len(raw_line)
                    summary["bytes_read"] += line_bytes
                    if not raw_line.strip():
                        continue
                    try:
                        value = json.loads(raw_line)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        record_error("session_json")
                        continue
                    category, is_compaction, is_tool_output, is_image = classify_session_record(value)
                    summary["records"] += 1
                    summary["category_counts"][category] = summary["category_counts"].get(category, 0) + 1
                    summary["category_bytes"][category] = summary["category_bytes"].get(category, 0) + line_bytes
                    if is_compaction:
                        summary["compaction_records"] += 1
                        summary["compaction_bytes"] += line_bytes
                    if is_tool_output:
                        summary["tool_output_records"] += 1
                        summary["tool_output_bytes"] += line_bytes
                    if is_image:
                        summary["image_records"] += 1
                        summary["image_bytes"] += line_bytes
        except OSError:
            record_error("session_read")
    return summary


def scan_codex_home(
    root: Path,
    max_entries: int = 1_000_000,
    since: datetime | None = None,
    session_overhead: bool = False,
    session_top: int = 3,
) -> dict[str, Any]:
    root = root.expanduser().resolve(strict=False)
    if not root.exists():
        raise FileNotFoundError(f"Codex home does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Codex home is not a directory: {root}")
    if session_top < 1:
        raise ValueError("session_top must be at least 1")
    if since is not None and since.tzinfo is None:
        raise ValueError("since must include a timezone")

    worktree_roots, worktree_errors = count_worktree_roots(root)
    result: dict[str, Any] = {
        "codex_home": str(root),
        **new_file_totals(),
        "directories": 0,
        "links_skipped": 0,
        "errors": worktree_errors,
        "error_kinds": {name: 0 for name in ERROR_KINDS},
        "entries_scanned": 0,
        "truncated": False,
        "database_like": {"files": 0, "bytes": 0},
        "worktree_roots": worktree_roots,
        "categories": {},
    }
    result["error_kinds"]["worktree"] = worktree_errors

    def record_error(kind: str) -> None:
        result["errors"] += 1
        result["error_kinds"][kind] += 1

    categories: dict[str, dict[str, Any]] = result["categories"]
    seen: set[tuple[int, int]] = set()
    category_seen: dict[str, set[tuple[int, int]]] = {}
    recent: dict[str, Any] | None = None
    recent_seen: set[tuple[int, int]] = set()
    recent_category_seen: dict[str, set[tuple[int, int]]] = {}
    if since is not None:
        recent = {
            "since_utc": since.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
            **new_file_totals(),
            "categories": {},
        }
        result["since"] = recent

    session_candidates: list[tuple[int, str, float]] = []
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
                        record_error("stat")
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
                        allocated = allocated_file_bytes(item_stat)
                        identity = file_identity(item_stat)
                        add_file(result, size, allocated, identity, seen)
                        add_file(category, size, allocated, identity, category_seen.setdefault(bucket, set()))
                        if is_database_like(entry.name):
                            result["database_like"]["files"] += 1
                            result["database_like"]["bytes"] += size

                        if recent is not None and item_stat.st_mtime >= since.timestamp():
                            recent_category = recent["categories"].setdefault(bucket, new_file_totals())
                            add_file(recent, size, allocated, identity, recent_seen)
                            add_file(
                                recent_category,
                                size,
                                allocated,
                                identity,
                                recent_category_seen.setdefault(bucket, set()),
                            )

                        if session_overhead and bucket in SESSION_BUCKETS and entry.name.lower().endswith(".jsonl"):
                            candidate = (size, entry.path, item_stat.st_mtime)
                            if len(session_candidates) < session_top:
                                heapq.heappush(session_candidates, candidate)
                            elif candidate[:2] > session_candidates[0][:2]:
                                heapq.heapreplace(session_candidates, candidate)
        except OSError:
            record_error("scandir")

    finalize_totals(result)
    for category in categories.values():
        finalize_totals(category)
    if recent is not None:
        finalize_totals(recent)
        for category in recent["categories"].values():
            finalize_totals(category)
    if session_overhead:
        result["session_overhead"] = analyze_session_candidates(session_candidates, record_error)
    return result


def human_bytes(value: int) -> str:
    units = ("B", "KiB", "MiB", "GiB", "TiB")
    size = float(value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    raise AssertionError("unreachable")


def display_bytes(value: int | None) -> str:
    return "n/a" if value is None else human_bytes(value)


def render_table(result: dict[str, Any], top: int) -> str:
    error_kinds = ", ".join(f"{name}={count}" for name, count in result["error_kinds"].items() if count)
    lines = [
        f"Codex home: {result['codex_home']}",
        f"Total apparent: {human_bytes(result['bytes'])}, unique: {human_bytes(result['unique_bytes'])}, "
        f"allocated: {display_bytes(result['allocated_bytes'])}",
        f"Entries: {result['files']} files, {result['directories']} directories, "
        f"{result['hardlink_duplicates']} duplicate hardlink references",
        f"Scan: {result['entries_scanned']} entries, {result['links_skipped']} links/junctions skipped, "
        f"{result['errors']} errors, truncated={str(result['truncated']).lower()}",
        f"Error kinds: {error_kinds or 'none'}",
        f"Database-like files: {result['database_like']['files']} totaling {human_bytes(result['database_like']['bytes'])}",
        f"Immediate worktree directories: {result['worktree_roots']}",
        "",
        "Top-level category             Apparent     Unique  Allocated      Files       Dirs  Links",
        "-----------------------------------------------------------------------------------------",
    ]
    ordered = sorted(result["categories"].items(), key=lambda item: (item[1]["bytes"], item[1]["files"]), reverse=True)
    for name, values in ordered[:top]:
        display = name if len(name) <= 28 else name[:25] + "..."
        lines.append(
            f"{display:<28} {human_bytes(values['bytes']):>10} {human_bytes(values['unique_bytes']):>10} "
            f"{display_bytes(values['allocated_bytes']):>10} {values['files']:>10} "
            f"{values['directories']:>10} {values['links_skipped']:>6}"
        )

    if "since" in result:
        recent = result["since"]
        lines.extend(
            [
                "",
                f"Changed since {recent['since_utc']}: apparent {human_bytes(recent['bytes'])}, "
                f"unique {human_bytes(recent['unique_bytes'])}, allocated {display_bytes(recent['allocated_bytes'])}, "
                f"{recent['files']} files",
            ]
        )
        recent_ordered = sorted(
            recent["categories"].items(), key=lambda item: (item[1]["bytes"], item[1]["files"]), reverse=True
        )
        for name, values in recent_ordered[:top]:
            lines.append(f"  {name}: {human_bytes(values['bytes'])}, {values['files']} files")

    if "session_overhead" in result:
        overhead = result["session_overhead"]
        lines.extend(
            [
                "",
                f"Session overhead sample: {overhead['sampled_files']} largest JSONL files, "
                f"{human_bytes(overhead['bytes_read'])} read, {overhead['records']} records",
                f"  compaction={human_bytes(overhead['compaction_bytes'])}, "
                f"tool_output={human_bytes(overhead['tool_output_bytes'])}, "
                f"image={human_bytes(overhead['image_bytes'])}",
            ]
        )
        for item in overhead["largest_files"]:
            lines.append(
                f"  rank {item['rank']}: size={human_bytes(item['size'])}, mtime={item['mtime_utc']}"
            )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-home", type=Path, default=default_codex_home())
    parser.add_argument("--format", choices=("table", "json"), default="table")
    parser.add_argument("--top", type=int, default=20, help="Maximum top-level categories in table output.")
    parser.add_argument("--max-entries", type=int, default=1_000_000, help="Stop after this many entries; 0 disables the cap.")
    parser.add_argument("--since", type=parse_since, help="Summarize files modified since YYYY-MM-DD at 00:00 UTC.")
    parser.add_argument(
        "--session-overhead",
        action="store_true",
        help="Opt in to parsing aggregate envelopes from the largest session JSONL files.",
    )
    parser.add_argument("--session-top", type=int, default=3, help="Largest session JSONL files to sample (default: 3).")
    args = parser.parse_args()
    if args.top < 1:
        parser.error("--top must be at least 1")
    if args.max_entries < 0:
        parser.error("--max-entries cannot be negative")
    if args.session_top < 1:
        parser.error("--session-top must be at least 1")

    try:
        result = scan_codex_home(
            args.codex_home,
            args.max_entries,
            since=args.since,
            session_overhead=args.session_overhead,
            session_top=args.session_top,
        )
    except (FileNotFoundError, NotADirectoryError) as exc:
        parser.exit(2, f"error: {exc}\n")
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(render_table(result, args.top))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

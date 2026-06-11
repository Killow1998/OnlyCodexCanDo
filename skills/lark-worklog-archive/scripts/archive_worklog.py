#!/usr/bin/env python3
"""Archive daily work bullets into monthly Feishu/Lark worklog documents."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape as xml_escape
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows fallback
    fcntl = None

try:
    import msvcrt
except ImportError:  # pragma: no cover - POSIX fallback
    msvcrt = None


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
PRIVATE_REGISTRY = os.path.join(SKILL_DIR, "references", "monthly-docs.local.json")
DEFAULT_REGISTRY = os.path.join(os.path.expanduser("~"), ".config", "lark-worklog-archive", "monthly-docs.json")
DEFAULT_CACHE = os.path.join(os.path.expanduser("~"), ".cache", "lark-worklog-archive", "cache.json")
DEFAULT_FAILED_QUEUE = os.path.join(os.path.expanduser("~"), ".local", "state", "lark-worklog-archive", "failed-queue.jsonl")
LARK_CONTENT_INLINE_LIMIT = 8000
LARK_SECTION_REPLACE_ARG_LIMIT = 12000
LARK_CONTENT_TMP_DIR = ".lark-worklog-archive-tmp"
RUN_LARK_VERBOSE = bool(os.environ.get("LARK_WORKLOG_VERBOSE"))
DATE_HEADING = re.compile(r"(?m)^#{1,6} ((?:\d{4}-\d{2}-\d{2})|(?:\d{2}-\d{2}-\d{4}))\s*$")
INTERNAL_NOTE_ITEMS = {
    "今日通过 Codex/Agent 完成的工作",
    "后续记录格式",
    "每天记录：目标、使用 Agent 完成的开发内容、关键命令/文件、验证结果、遗留问题。",
    "同类内容合并到分类 bullet 下，具体工作作为二级无序列表记录。",
    "按事项记录背景与目标、工作内容、结果、问题与下一步；命令、文件、测试和提交只作为证据。",
    "约定每一天使用一级标题 `# YYYY-MM-DD`，标题下只写无序列表，不再使用二级标题或小节标题。",
}
BUILTIN_CATEGORY_ORDER = [
    "工作记录 / 知识管理",
    "Agent 工具 / 自动化",
    "开发环境 / 系统配置",
    "ROS / SLAM",
    "仿真 / 训练",
    "实机 / 硬件部署",
    "其他",
]
BUILTIN_SUBCATEGORY_ORDER = [
    "背景与目标",
    "工作内容",
    "结果",
    "问题与下一步",
]
BUILTIN_FALLBACK_CATEGORY = "其他"
BUILTIN_FALLBACK_SUBCATEGORY = "工作内容"
TEAM_SIGNED_SUBCATEGORY = "工作内容"
LEGACY_SUBCATEGORY_MAP = {
    "代码与仓库": "结果",
    "验证与测试": "结果",
    "开发环境": "工作内容",
    "问题与风险": "问题与下一步",
    "其他": "工作内容",
}
CATEGORY_ORDER = list(BUILTIN_CATEGORY_ORDER)
SUBCATEGORY_ORDER = list(BUILTIN_SUBCATEGORY_ORDER)
FALLBACK_CATEGORY = BUILTIN_FALLBACK_CATEGORY
FALLBACK_SUBCATEGORY = BUILTIN_FALLBACK_SUBCATEGORY


class ArchiveResult:
    def __init__(self, doc: str, title: str, date: str, item_count: int, dry_run: bool = False):
        self.doc = doc
        self.title = title
        self.date = date
        self.item_count = item_count
        self.dry_run = dry_run


class RepairResult:
    def __init__(self, doc: str, title: str, dates: list[str], changed: bool, dry_run: bool = False):
        self.doc = doc
        self.title = title
        self.dates = dates
        self.changed = changed
        self.dry_run = dry_run


def default_registry_path() -> str:
    if os.environ.get("LARK_WORKLOG_REGISTRY"):
        return os.environ["LARK_WORKLOG_REGISTRY"]
    if os.path.exists(PRIVATE_REGISTRY):
        return PRIVATE_REGISTRY
    return DEFAULT_REGISTRY


def default_cache_path() -> str:
    return os.environ.get("LARK_WORKLOG_CACHE", DEFAULT_CACHE)


def default_failed_queue_path() -> str:
    return os.environ.get("LARK_WORKLOG_FAILED_QUEUE", DEFAULT_FAILED_QUEUE)


def redact(value: str) -> str:
    value = re.sub(r"https?://[^\s)>\"]+", "<redacted-url>", value)
    value = re.sub(r"\bou_[A-Za-z0-9_-]{8,}\b", "<redacted-open-id>", value)
    value = re.sub(r"\bcli_[A-Za-z0-9_-]{8,}\b", "<redacted-app-id>", value)
    value = re.sub(
        r"(?i)\b((?:tenant_)?access[_-]?token|refresh[_-]?token|app[_-]?secret|secret)([\"'\s:=]+)([^,\s\"']+)",
        r"\1\2<redacted>",
        value,
    )
    value = re.sub(r"(?i)(Authorization\s*:\s*Bearer\s+)[A-Za-z0-9._~+/=-]+", r"\1<redacted>", value)
    return value


def print_redacted(value: str, file=None) -> None:
    if value:
        if file is None:
            file = sys.stderr
        print(redact(value), file=file, end="" if value.endswith("\n") else "\n")


def expanded_path(path: str) -> str:
    return os.path.abspath(os.path.expanduser(path))


def ensure_parent_dir(path: str) -> str:
    absolute = expanded_path(path)
    parent = os.path.dirname(absolute)
    if parent:
        os.makedirs(parent, exist_ok=True)
    return absolute


def lark_content_arg(content: str) -> tuple[str, str | None]:
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    if content.startswith("@") or len(content) <= LARK_CONTENT_INLINE_LIMIT:
        return content, None
    tmp_dir = os.path.join(os.getcwd(), LARK_CONTENT_TMP_DIR)
    os.makedirs(tmp_dir, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        newline="\n",
        delete=False,
        dir=tmp_dir,
        prefix="lark-worklog-content-",
        suffix=".xml",
    )
    try:
        handle.write(content)
        relative = os.path.relpath(handle.name, os.getcwd()).replace(os.sep, "/")
        return f"@./{relative}", handle.name
    finally:
        handle.close()


def lark_args_with_content_files(args: list[str]) -> tuple[list[str], list[str]]:
    result = list(args)
    cleanup: list[str] = []
    index = 0
    while index < len(result) - 1:
        if result[index] == "--content":
            value, temp_path = lark_content_arg(result[index + 1])
            result[index + 1] = value
            if temp_path:
                cleanup.append(temp_path)
            index += 2
            continue
        index += 1
    return result, cleanup


def compact_error(value: str, limit: int = 180) -> str:
    clean = " ".join(redact(value).split())
    if len(clean) > limit:
        return f"{clean[: limit - 3]}..."
    return clean


def lark_cli_command() -> str | None:
    configured = os.environ.get("LARK_CLI")
    if configured:
        return configured
    names = ("lark-cli.cmd", "lark-cli.exe", "lark-cli") if os.name == "nt" else ("lark-cli",)
    for name in names:
        path = shutil.which(name)
        if path:
            return path
    return None


def codex_managed_lark_root() -> str | None:
    configured = os.environ.get("LARK_WORKLOG_LARK_RUNTIME_ROOT")
    if configured:
        return os.path.abspath(os.path.expanduser(configured))
    if os.environ.get("CODEX_THREAD_ID") or os.environ.get("CODEX_CI") == "1":
        return os.path.join(os.path.expanduser("~"), ".codex", "memories", "runtime", "lark-cli")
    return None


def legacy_lark_config_dir() -> str:
    return os.path.join(os.path.expanduser("~"), ".lark-cli")


def legacy_lark_data_dir() -> str:
    return os.path.join(os.path.expanduser("~"), ".local", "share", "lark-cli")


def copy_tree_if_missing(source: str, target: str) -> None:
    if not os.path.isdir(source) or os.path.exists(target):
        return
    os.makedirs(os.path.dirname(target), exist_ok=True)
    shutil.copytree(source, target, copy_function=shutil.copy2)


def lark_cli_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("LARK_CLI_NO_PROXY", "1")
    runtime_root = codex_managed_lark_root()
    if not runtime_root:
        return env
    config_dir = env.get("LARKSUITE_CLI_CONFIG_DIR") or os.path.join(runtime_root, "config")
    data_dir = env.get("LARKSUITE_CLI_DATA_DIR") or os.path.join(runtime_root, "data")
    if "LARKSUITE_CLI_CONFIG_DIR" not in env:
        copy_tree_if_missing(legacy_lark_config_dir(), config_dir)
        env["LARKSUITE_CLI_CONFIG_DIR"] = config_dir
    if "LARKSUITE_CLI_DATA_DIR" not in env:
        # The released lark-cli treats LARKSUITE_CLI_DATA_DIR as a base path
        # and appends its own service directory ("lark-cli") underneath it.
        copy_tree_if_missing(legacy_lark_data_dir(), os.path.join(data_dir, "lark-cli"))
        env["LARKSUITE_CLI_DATA_DIR"] = data_dir
    return env


def run_lark(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    env = lark_cli_env()
    command = lark_cli_command()
    if not command:
        raise SystemExit("lark-cli not found. Run: npx @larksuite/cli@latest install")
    final_args, cleanup = lark_args_with_content_files(args)
    try:
        proc = subprocess.run(
            [command, *final_args],
            env=env,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    finally:
        for path in cleanup:
            try:
                os.unlink(path)
            except OSError:
                pass
    if check and proc.returncode != 0:
        if proc.stderr:
            print_redacted(proc.stderr)
        if proc.stdout:
            print_redacted(proc.stdout)
        raise SystemExit(proc.returncode)
    if check and proc.stderr and RUN_LARK_VERBOSE:
        print_redacted(proc.stderr)
    return proc


@contextmanager
def month_lock(key: str, enabled: bool = True):
    if not enabled:
        yield
        return
    path = os.path.join(tempfile.gettempdir(), f"lark-worklog-archive-{key}.lock")
    with open(path, "a+b") as handle:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        if fcntl is not None:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        elif msvcrt is not None:
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        try:
            yield
        finally:
            handle.seek(0)
            if fcntl is not None:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            elif msvcrt is not None:
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)


def today(tz_name: str) -> dt.date:
    try:
        tzinfo = ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        if tz_name == "Asia/Shanghai":
            tzinfo = dt.timezone(dt.timedelta(hours=8), name="Asia/Shanghai")
        elif tz_name.upper() == "UTC":
            tzinfo = dt.timezone.utc
        else:
            raise SystemExit(
                f"Timezone data not found for {tz_name!r}. Install the Python tzdata package or pass --tz UTC."
            )
    return dt.datetime.now(tzinfo).date()


def parse_date(value: str) -> dt.date:
    for fmt in ("%Y-%m-%d", "%m-%d-%Y"):
        try:
            return dt.datetime.strptime(value, fmt).date()
        except ValueError:
            pass
    raise SystemExit("--date must use YYYY-MM-DD or MM-DD-YYYY")


def display_date(value: dt.date) -> str:
    return value.strftime("%m-%d-%Y")


def month_key(value: dt.date) -> str:
    return value.strftime("%Y-%m")


def month_title(value: dt.date) -> str:
    return value.strftime("%m-%Y 工作记录")


def document_title(value: dt.date, metadata: dict | None = None) -> str:
    prefix = ""
    if metadata and isinstance(metadata.get("doc_title_prefix"), str):
        prefix = metadata["doc_title_prefix"].strip()
    base = month_title(value)
    return f"{prefix} {base}".strip() if prefix else base


def read_items(args: argparse.Namespace) -> list[str]:
    raw: list[str] = []
    raw.extend(args.item or [])
    if args.content:
        raw.extend(args.content.splitlines())
    if not raw and not sys.stdin.isatty():
        raw.extend(sys.stdin.read().splitlines())

    items: list[str] = []
    for line in raw:
        text = line.strip()
        if not text:
            continue
        if text.startswith("- "):
            items.append(text)
        else:
            items.append(f"- {text}")
    if not items:
        raise SystemExit("No archive items provided. Use --item, --content, or stdin.")
    return items


def is_date_heading(line: str) -> bool:
    return bool(re.match(r"^# (?:\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4})\s*$", line))


def normalize_date_heading(value: str) -> str:
    return display_date(parse_date(value))


def strip_non_date_title(markdown: str) -> str:
    lines = markdown.strip().splitlines()
    if lines and re.fullmatch(r"<title(?:\s+[^>]*)?>.*</title>", lines[0].strip()):
        return "\n".join(lines[1:]).lstrip()
    if lines and lines[0].startswith("# ") and not is_date_heading(lines[0]):
        return "\n".join(lines[1:]).lstrip()
    return markdown.strip()


def split_sections(markdown: str) -> list[tuple[str | None, str]]:
    markdown = strip_non_date_title(markdown)
    matches = list(DATE_HEADING.finditer(markdown))
    if not matches:
        return [(None, markdown.strip())] if markdown.strip() else []

    sections: list[tuple[str | None, str]] = []
    prefix = markdown[: matches[0].start()].strip()
    if prefix:
        sections.append((None, prefix))
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        sections.append((normalize_date_heading(match.group(1)), markdown[match.start() : end].strip()))
    return sections


def normalize_section_body(section: str) -> list[str]:
    lines = section.splitlines()[1:]
    bullets: list[str] = []
    for line in lines:
        text = line.strip()
        if not text:
            continue
        if text.startswith("#"):
            bullets.append(f"- {text.lstrip('#').strip()}")
        elif text.startswith("- "):
            bullets.append(text)
        else:
            bullets.append(f"- {text}")
    return bullets


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def strip_item_marker(item: str) -> str:
    return item[2:].strip() if item.startswith("- ") else item.strip()


def canonical_subcategory_name(name: str) -> str | None:
    clean = name.strip()
    if clean in SUBCATEGORY_ORDER:
        return clean
    return LEGACY_SUBCATEGORY_MAP.get(clean)


def split_category_prefix(item: str) -> tuple[str | None, str | None, str]:
    text = strip_item_marker(item)
    if "::" in text:
        parts = [part.strip() for part in text.split("::") if part.strip()]
        if len(parts) >= 3:
            return parts[0], canonical_subcategory_name(parts[1]) or parts[1], "::".join(parts[2:]).strip()
        if len(parts) == 2:
            if parts[0] in CATEGORY_ORDER:
                return parts[0], None, parts[1]
            subcategory = canonical_subcategory_name(parts[0])
            if subcategory:
                return None, subcategory, parts[1]
            return parts[0], None, parts[1]
    if "：" in text:
        category, content = text.split("：", 1)
        category = category.strip()
        content = content.strip()
        if category in CATEGORY_ORDER and content:
            return category, None, content
        subcategory = canonical_subcategory_name(category)
        if subcategory and content:
            return None, subcategory, content
    return None, None, text


def categorize_item(item: str) -> str:
    explicit, _, _ = split_category_prefix(item)
    return explicit or FALLBACK_CATEGORY


def preserve_or_default_category(current_category: str | None, item: str) -> str:
    return current_category or categorize_item(item)


def subcategorize_item(item: str) -> str:
    _, explicit, _ = split_category_prefix(item)
    return explicit or FALLBACK_SUBCATEGORY


def canonical_item(item: str) -> str:
    _, _, text = split_category_prefix(item)
    # Lark Markdown fetches may repeatedly escape Markdown punctuation.
    # Do not collapse ordinary path backslashes; only unescape punctuation.
    text = re.sub(r"\\+([`<>\[\]()_~*])", r"\1", text)
    return text.strip()


def verification_key(item: str) -> str:
    text = canonical_item(item)
    # Lark Markdown may round-trip Windows paths with different escaping.
    # Verification should prove the content is present, not enforce a backslash style.
    text = re.sub(r"\\+", r"\\", text)
    return text


def markdown_section_replace_is_risky(section: str) -> bool:
    # Feeding fetched Markdown back through str_replace can amplify escapes.
    return bool(
        "\\" in section
        or re.search(r"(^|[^\\])__(?=\S)", section)
        or re.search(r"(^|[^\\])\*\*(?=\S)", section)
    )


def inline_markdown_to_xml(text: str) -> str:
    result: list[str] = []
    cursor = 0
    pattern = re.compile(r"\[([^\]\n]+)\]\((https?://[^)\s]+)\)")
    for match in pattern.finditer(text):
        result.append(xml_escape(text[cursor : match.start()]))
        label = xml_escape(match.group(1))
        url = xml_escape(match.group(2), {'"': "&quot;"})
        result.append(f'<a href="{url}">{label}</a>')
        cursor = match.end()
    result.append(xml_escape(text[cursor:]))
    return "".join(result)


def has_author_signature(text: str) -> bool:
    clean = text.strip()
    if re.match(r"^[A-Za-z]:[\\/]", clean):
        return False
    return bool(re.match(r"^[^：:\s][^：:]{0,31}[：:]\s*\S+", clean))


def author_name(args: argparse.Namespace, metadata: dict) -> str | None:
    value = args.author or os.environ.get("LARK_WORKLOG_AUTHOR") or metadata.get("default_author")
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def sign_team_items(items: list[str], metadata: dict, author: str | None) -> list[str]:
    if metadata.get("mode") != "team":
        return items
    result: list[str] = []
    for item in items:
        category, subcategory, text = split_category_prefix(item)
        final_category = category or categorize_item(text)
        final_subcategory = subcategory or subcategorize_item(text)
        clean = canonical_item(text)
        if final_subcategory == TEAM_SIGNED_SUBCATEGORY and clean and not has_author_signature(clean):
            if not author:
                raise SystemExit("Team work content requires --author or LARK_WORKLOG_AUTHOR so entries can be attributed.")
            clean = f"{author}：{clean}"
        result.append(f"{final_category}::{final_subcategory}::{clean}")
    return result


def is_internal_note_item(item: str) -> bool:
    return canonical_item(item) in INTERNAL_NOTE_ITEMS


def ordered_categories(categories: dict[str, dict[str, list[str]]]) -> list[str]:
    known = [category for category in CATEGORY_ORDER if category in categories]
    extra = sorted(category for category in categories if category not in CATEGORY_ORDER)
    return [*known, *extra]


def ordered_subcategories(categories: dict[str, list[str]]) -> list[str]:
    known = [category for category in SUBCATEGORY_ORDER if category in categories]
    extra = sorted(category for category in categories if category not in SUBCATEGORY_ORDER)
    return [*known, *extra]


def add_group_item(groups: dict[str, dict[str, list[str]]], category: str, subcategory: str, item: str) -> None:
    if is_internal_note_item(item):
        return
    groups.setdefault(category, {})
    groups[category].setdefault(subcategory, [])
    existing = {canonical_item(old) for old in groups[category][subcategory]}
    if canonical_item(item) not in existing:
        groups[category][subcategory].append(f"- {canonical_item(item)}")


def group_items(items: list[str]) -> dict[str, dict[str, list[str]]]:
    groups: dict[str, dict[str, list[str]]] = {}
    for item in items:
        category, subcategory, text = split_category_prefix(item)
        add_group_item(groups, category or categorize_item(text), subcategory or subcategorize_item(text), text)
    return groups


def merge_groups(
    base: dict[str, dict[str, list[str]]],
    incoming: dict[str, dict[str, list[str]]],
) -> dict[str, dict[str, list[str]]]:
    merged = {category: {sub: list(items) for sub, items in subgroups.items()} for category, subgroups in base.items()}
    for category, subgroups in incoming.items():
        for subcategory, items in subgroups.items():
            for item in items:
                add_group_item(merged, category, subcategory, item)
    return merged


def render_day_section(date: str, groups: dict[str, dict[str, list[str]]]) -> str:
    lines = [f"# {date}", ""]
    for category in ordered_categories(groups):
        subgroups = groups[category]
        if not any(items for items in subgroups.values()):
            continue
        lines.append(f"- {category}")
        for subcategory in ordered_subcategories(subgroups):
            items = [item for item in subgroups[subcategory] if not is_internal_note_item(item)]
            if not items:
                continue
            lines.append(f"  - {subcategory}")
            lines.extend(f"    - {canonical_item(item)}" for item in items)
    return "\n".join(lines).strip()


def bullet_level(line: str) -> int | None:
    match = re.match(r"^(\s*)-\s+(.+?)\s*$", line)
    if not match:
        return None
    return match.group(1).replace("\t", "  ").count(" ") // 2


def bullet_text(line: str) -> str:
    return re.sub(r"^\s*-\s+", "", line).strip()


def normalize_section_groups(section: str) -> dict[str, dict[str, list[str]]]:
    lines = section.splitlines()[1:]
    groups: dict[str, dict[str, list[str]]] = {}
    current_category: str | None = None
    current_subcategory: str | None = None
    index = 0
    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()
        if not stripped:
            index += 1
            continue
        if stripped.startswith("#"):
            text = stripped.lstrip("#").strip()
            add_group_item(groups, categorize_item(text), subcategorize_item(text), text)
            current_category = None
            current_subcategory = None
            index += 1
            continue
        level = bullet_level(raw)
        if level is not None:
            text = bullet_text(raw)
            next_level = None
            probe = index + 1
            while probe < len(lines):
                next_raw = lines[probe]
                if not next_raw.strip():
                    probe += 1
                    continue
                next_level = bullet_level(next_raw)
                break
            has_child = next_level is not None and next_level > level
            if level == 0 and has_child:
                if text == "其他":
                    current_category = None
                    current_subcategory = None
                elif canonical_subcategory_name(text) and text not in CATEGORY_ORDER:
                    current_category = None
                    current_subcategory = canonical_subcategory_name(text)
                else:
                    current_category = text
                    current_subcategory = None
                    groups.setdefault(current_category, {})
            elif level == 1 and has_child:
                if current_category:
                    current_subcategory = canonical_subcategory_name(text) or subcategorize_item(text)
                    groups[current_category].setdefault(current_subcategory, [])
                else:
                    current_subcategory = canonical_subcategory_name(text) or subcategorize_item(text)
            else:
                category, subcategory, content = split_category_prefix(text)
                if content in CATEGORY_ORDER or canonical_subcategory_name(content):
                    index += 1
                    continue
                if level == 0:
                    target_category = category or categorize_item(content)
                    target_subcategory = subcategory or subcategorize_item(content)
                elif current_category and current_subcategory and level > 1:
                    target_category = category or preserve_or_default_category(current_category, content)
                    target_subcategory = current_subcategory
                elif current_category:
                    target_category = category or preserve_or_default_category(current_category, content)
                    target_subcategory = subcategory or subcategorize_item(content)
                elif current_subcategory:
                    target_category = category or preserve_or_default_category(None, content)
                    target_subcategory = current_subcategory
                else:
                    target_category = category or preserve_or_default_category(None, content)
                    target_subcategory = subcategory or subcategorize_item(content)
                add_group_item(groups, target_category, target_subcategory, content)
                if level == 0:
                    current_category = None
                    current_subcategory = None
            index += 1
            continue
        add_group_item(groups, preserve_or_default_category(None, stripped), subcategorize_item(stripped), stripped)
        current_category = None
        current_subcategory = None
        index += 1
    return groups


def normalize_date_section(section_date: str, section: str) -> str:
    return render_day_section(section_date, normalize_section_groups(section))


def merge_document(current: str, date: str, new_items: list[str]) -> str:
    old_groups: dict[str, dict[str, list[str]]] = {}
    remaining: list[str] = []
    for section_date, section in split_sections(current):
        if section_date == date:
            old_groups = merge_groups(old_groups, normalize_section_groups(section))
        elif section_date is None:
            old_groups = merge_groups(old_groups, group_items(normalize_section_body(section)))
        elif section.strip():
            remaining.append(normalize_date_section(section_date, section))

    clean_new_items = [item for item in new_items if not is_internal_note_item(item)]
    new_groups = merge_groups(old_groups, group_items(clean_new_items))
    new_section = render_day_section(date, new_groups)
    parts = [new_section, *remaining]
    return "\n\n".join(part for part in parts if part).strip() + "\n"


def normalize_document_sections(current: str) -> str:
    sections = []
    for section_date, section in split_sections(current):
        if section_date and section.strip():
            sections.append(normalize_date_section(section_date, section))
    return "\n\n".join(sections).strip() + "\n" if sections else ""


def section_signature(section: str) -> dict[str, dict[str, list[str]]]:
    groups = normalize_section_groups(section)
    return {
        category: {
            subcategory: [verification_key(item) for item in items]
            for subcategory, items in subgroups.items()
            if items
        }
        for category, subgroups in groups.items()
        if any(items for items in subgroups.values())
    }


def replace_document_section(current: str, target_date: str, replacement: str) -> str:
    sections: list[str] = []
    replaced = False
    for section_date, section in split_sections(current):
        if not section_date:
            continue
        if section_date == target_date:
            sections.append(replacement.strip())
            replaced = True
        elif section.strip():
            sections.append(section.strip())
    if not replaced:
        raise SystemExit(f"No section found for {target_date}. Use --all-dates to repair the whole month.")
    return "\n\n".join(sections).strip() + "\n" if sections else ""


def top_level_repair_notes(section_date: str, section: str) -> list[str]:
    notes: list[str] = []
    lines = section.splitlines()[1:]
    visual_escape_count = 0
    for index, raw in enumerate(lines):
        if re.search(r"\\{4,}", raw) or re.search(r"\\+\*", raw):
            visual_escape_count += 1
        if bullet_level(raw) != 0:
            continue
        text = bullet_text(raw)
        probe = index + 1
        next_level = None
        while probe < len(lines):
            next_raw = lines[probe]
            if not next_raw.strip():
                probe += 1
                continue
            next_level = bullet_level(next_raw)
            break
        has_child = next_level is not None and next_level > 0
        if not has_child:
            continue
        mapped_subcategory = canonical_subcategory_name(text)
        if mapped_subcategory and text not in CATEGORY_ORDER:
            notes.append(f"{section_date}: moved top-level subcategory '{text}' to fallback '{FALLBACK_CATEGORY}/{mapped_subcategory}'")
    groups = normalize_section_groups(section)
    unknown = [
        canonical_item(item)
        for item in groups.get(FALLBACK_CATEGORY, {}).get(FALLBACK_SUBCATEGORY, [])
    ]
    if unknown:
        preview = "; ".join(unknown[:3])
        suffix = "" if len(unknown) <= 3 else f"; +{len(unknown) - 3} more"
        notes.append(f"{section_date}: {len(unknown)} item(s) remain in fallback '{FALLBACK_CATEGORY}/{FALLBACK_SUBCATEGORY}': {preview}{suffix}")
    if visual_escape_count:
        notes.append(f"{section_date}: {visual_escape_count} item(s) contain excessive Markdown/Windows path escaping")
    return notes


def repair_notes(current: str, target_date: str | None = None) -> list[str]:
    notes: list[str] = []
    for section_date, section in split_sections(current):
        if not section_date or not section.strip():
            continue
        if target_date and section_date != target_date:
            continue
        notes.extend(top_level_repair_notes(section_date, section))
    return notes


def markdown_to_xml(markdown: str, title: str) -> str:
    parts = [f"<title>{xml_escape(title)}</title>"]
    for section_date, section in split_sections(markdown):
        if section_date is None:
            continue
        groups = normalize_section_groups(section)
        parts.append(f"<h1>{xml_escape(section_date)}</h1>")
        category_parts: list[str] = []
        for category in ordered_categories(groups):
            subgroups = groups[category]
            if not any(items for items in subgroups.values()):
                continue
            subcategory_parts: list[str] = []
            for subcategory in ordered_subcategories(subgroups):
                items = subgroups[subcategory]
                if not items:
                    continue
                item_xml = "".join(f"<li>{inline_markdown_to_xml(canonical_item(item))}</li>" for item in items)
                subcategory_parts.append(f"<li>{xml_escape(subcategory)}<ul>{item_xml}</ul></li>")
            category_parts.append(f"<li>{xml_escape(category)}<ul>{''.join(subcategory_parts)}</ul></li>")
        if category_parts:
            parts.append("<ul>" + "".join(category_parts) + "</ul>")
    return "".join(parts)


def fetch_doc(doc: str) -> tuple[str, int]:
    proc = run_lark(
        [
            "docs",
            "+fetch",
            "--api-version",
            "v2",
            "--as",
            "user",
            "--doc",
            doc,
            "--doc-format",
            "markdown",
        ]
    )
    payload = json.loads(proc.stdout)
    document = payload["data"]["document"]
    content = str(document.get("content", "")).replace("\r\n", "\n").replace("\r", "\n")
    return content, int(document.get("revision_id", -1))


def fetch_doc_xml(doc: str) -> tuple[str, int]:
    proc = run_lark(
        [
            "docs",
            "+fetch",
            "--api-version",
            "v2",
            "--as",
            "user",
            "--doc",
            doc,
            "--detail",
            "with-ids",
        ]
    )
    payload = json.loads(proc.stdout)
    document = payload["data"]["document"]
    return document.get("content", ""), int(document.get("revision_id", -1))


def parse_blocks(xml_content: str) -> list[dict[str, str]]:
    try:
        root = ET.fromstring(f"<root>{xml_content}</root>")
    except ET.ParseError:
        return []
    blocks: list[dict[str, str]] = []
    for child in list(root):
        text = "".join(child.itertext()).strip()
        blocks.append({"tag": child.tag, "id": child.attrib.get("id", ""), "text": html.unescape(text)})
    return blocks


def find_heading_id(xml_content: str, date: str) -> str | None:
    for block in parse_blocks(xml_content):
        if block["tag"] in {"title", "h1"} and block["text"] == date and block["id"]:
            return block["id"]
    return None


def find_title_id(xml_content: str) -> str | None:
    for block in parse_blocks(xml_content):
        if block["tag"] == "title" and block["id"]:
            return block["id"]
    return None


def create_doc(title: str, content_xml: str) -> str:
    proc = run_lark(
        [
            "docs",
            "+create",
            "--api-version",
            "v2",
            "--as",
            "user",
            "--content",
            content_xml,
        ]
    )
    payload = json.loads(proc.stdout)
    document = payload["data"]["document"]
    doc = document.get("url") or document["document_id"]
    return doc


def iter_dicts(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from iter_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_dicts(child)


def strip_tags(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value).strip()


def find_url(value: dict) -> str | None:
    for key in ("url", "docs_url", "doc_url", "web_url", "link"):
        found = value.get(key)
        if isinstance(found, str) and found.startswith("http"):
            return found
    token = value.get("token") or value.get("obj_token") or value.get("file_token")
    if isinstance(token, str) and token:
        return token
    for child in value.values():
        if isinstance(child, dict):
            nested = find_url(child)
            if nested:
                return nested
        elif isinstance(child, list):
            for item in child:
                if isinstance(item, dict):
                    nested = find_url(item)
                    if nested:
                        return nested
    return None


def search_docs_by_title(title: str) -> list[dict]:
    attempts = [
        (
            f'intitle:"{title}"',
            '{"only_title":true,"doc_types":["DOC","DOCX"]}',
        ),
        (
            title,
            '{"only_title":true,"doc_types":["DOC","DOCX"]}',
        ),
        (
            title,
            None,
        ),
    ]
    matches: list[dict] = []
    seen: set[str] = set()
    for query, filter_value in attempts:
        args = [
            "docs",
            "+search",
            "--as",
            "user",
            "--query",
            query,
            "--page-size",
            "10",
        ]
        if filter_value:
            args.extend(["--filter", filter_value])
        proc = run_lark(args, check=False)
        if proc.returncode != 0:
            continue
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError:
            continue
        for item in iter_dicts(payload):
            candidate_title = item.get("title") or item.get("name") or item.get("title_highlighted")
            if not isinstance(candidate_title, str) or strip_tags(candidate_title) != title:
                continue
            url = find_url(item)
            if not url or url in seen:
                continue
            seen.add(url)
            matches.append(item)
        if matches:
            break
    return matches


def find_doc_by_title(title: str) -> str | None:
    for item in search_docs_by_title(title):
        url = find_url(item)
        if url:
            return url
    return None


def update_doc(doc: str, content_xml: str, revision_id: int, title: str | None = None) -> bool:
    args = [
        "docs",
        "+update",
        "--api-version",
        "v2",
        "--as",
        "user",
        "--doc",
        doc,
        "--revision-id",
        str(revision_id),
        "--command",
        "overwrite",
        "--content",
        content_xml,
    ]
    if title:
        args.extend(["--new-title", title])
    proc = run_lark(args, check=False)
    if proc.returncode == 0:
        return True
    if proc.stderr:
        print_redacted(proc.stderr)
    if proc.stdout:
        print_redacted(proc.stdout)
    return False


def update_section(doc: str, pattern: str, content: str, revision_id: int) -> bool:
    proc = run_lark(
        [
            "docs",
            "+update",
            "--api-version",
            "v2",
            "--as",
            "user",
            "--doc",
            doc,
            "--revision-id",
            str(revision_id),
            "--command",
            "str_replace",
            "--doc-format",
            "markdown",
            "--pattern",
            pattern,
            "--content",
            content,
        ],
        check=False,
    )
    return proc.returncode == 0


def section_replace_args_are_safe(pattern: str, content: str) -> bool:
    return len(pattern) + len(content) <= LARK_SECTION_REPLACE_ARG_LIMIT


def day_section_to_xml(date: str, groups: dict[str, dict[str, list[str]]]) -> str:
    xml = [f"<h1>{xml_escape(date)}</h1>"]
    category_parts: list[str] = []
    for category in ordered_categories(groups):
        subgroups = groups[category]
        if not any(items for items in subgroups.values()):
            continue
        subcategory_parts: list[str] = []
        for subcategory in ordered_subcategories(subgroups):
            items = subgroups[subcategory]
            if not items:
                continue
            item_xml = "".join(f"<li>{inline_markdown_to_xml(canonical_item(item))}</li>" for item in items)
            subcategory_parts.append(f"<li>{xml_escape(subcategory)}<ul>{item_xml}</ul></li>")
        category_parts.append(f"<li>{xml_escape(category)}<ul>{''.join(subcategory_parts)}</ul></li>")
    if category_parts:
        xml.append("<ul>" + "".join(category_parts) + "</ul>")
    return "".join(xml)


def insert_after_block(doc: str, block_id: str, content_xml: str, revision_id: int) -> bool:
    proc = run_lark(
        [
            "docs",
            "+update",
            "--api-version",
            "v2",
            "--as",
            "user",
            "--doc",
            doc,
            "--revision-id",
            str(revision_id),
            "--command",
            "block_insert_after",
            "--block-id",
            block_id,
            "--content",
            content_xml,
        ],
        check=False,
    )
    return proc.returncode == 0


def verify_items(doc: str, date: str, items: list[str]) -> int:
    content, revision_id = fetch_doc(doc)
    sections = dict(split_sections(content))
    section = sections.get(date, "")
    section_groups = normalize_section_groups(section)
    section_items = {
        verification_key(item)
        for subgroups in section_groups.values()
        for sub_items in subgroups.values()
        for item in sub_items
    }
    missing = [canonical_item(item) for item in items if verification_key(item) not in section_items]
    if missing:
        raise SystemExit(f"Verification failed; missing archived item(s): {missing}")
    return revision_id


def auth_status_payload() -> tuple[dict | None, str | None]:
    proc = run_lark(["auth", "status"], check=False)
    if proc.returncode != 0:
        return None, compact_error(proc.stderr or proc.stdout or "auth status failed")
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None, "auth status returned non-JSON output"
    return payload if isinstance(payload, dict) else None, None


def authorized_user_open_id(payload: dict) -> tuple[str | None, str | None]:
    identities = payload.get("identities")
    user = identities.get("user") if isinstance(identities, dict) else None
    if isinstance(user, dict):
        open_id = user.get("openId")
        token_status = str(user.get("tokenStatus") or "")
        status = str(user.get("status") or "")
        if open_id and (user.get("available") is True or token_status == "valid" or status == "ready"):
            return str(open_id), None
        detail = str(user.get("message") or "")
        if detail:
            return None, detail
        if open_id:
            return None, f"user identity not authorized: status={status or 'unknown'}, tokenStatus={token_status or 'unknown'}"

    detail = str(payload.get("note") or payload.get("message") or "")
    return None, detail or "no authorized user identity"


def auth_fix_hint(error: str | None = None) -> str:
    base = 'lark-cli auth login --recommend --domain docs,drive,markdown --scope "search:docs:read"'
    lowered = (error or "").lower()
    if os.name == "nt" and ("keychain" in lowered or "no token" in lowered):
        return (
            "Windows Codex sandbox may not be able to read the lark-cli 1.0.51 credential store. "
            f"First verify outside the sandbox with `{base}` or `lark-cli auth status`; "
            "if that succeeds but this doctor still fails, run real Feishu operations with approved non-sandbox execution."
        )
    return base


def current_user_open_id() -> str | None:
    payload, _ = auth_status_payload()
    if not payload:
        return None
    value, _ = authorized_user_open_id(payload)
    return value


def load_registry_payload(path: str) -> dict:
    path = expanded_path(path)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8-sig") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        return {}
    return payload


def load_registry(path: str) -> tuple[dict[str, str], str | None]:
    payload = load_registry_payload(path)
    if not payload:
        return {}, None
    docs = payload.get("docs")
    if docs is None:
        docs = {key: value for key, value in payload.items() if re.fullmatch(r"\d{4}-\d{2}", str(key))}
    if not isinstance(docs, dict):
        docs = {}
    owner = payload.get("owner_open_id")
    return {str(key): str(value) for key, value in docs.items()}, str(owner) if owner else None


def load_registry_metadata(path: str) -> dict:
    payload = load_registry_payload(path)
    reserved = {"schema_version", "owner_open_id", "title_template", "date_heading_template", "docs"}
    return {key: value for key, value in payload.items() if key not in reserved}


def normalized_registry_metadata(args: argparse.Namespace, metadata: dict, user_open_id: str | None = None) -> dict:
    result = dict(metadata)
    if args.team or result.get("mode") == "team":
        result["mode"] = "team"
        team_id = args.team_id or result.get("team_id")
        if not team_id:
            raise SystemExit("Team registry mode requires --team-id during initialization.")
        result["team_id"] = str(team_id)
        if args.title_prefix is not None:
            result["doc_title_prefix"] = args.title_prefix.strip()
        elif "doc_title_prefix" not in result:
            result["doc_title_prefix"] = str(team_id)
        result["share_policy"] = args.share_policy or result.get("share_policy") or "manual"
        allowed = [str(item) for item in result.get("allowed_user_open_ids", []) if str(item)]
        for item in args.allow_user_open_id or []:
            if item not in allowed:
                allowed.append(item)
        if user_open_id and user_open_id not in allowed:
            allowed.append(user_open_id)
        result["allowed_user_open_ids"] = allowed
    elif result.get("mode") not in (None, "personal"):
        raise SystemExit("Registry mode must be 'personal' or 'team'.")
    else:
        result["mode"] = "personal"
    return result


def ensure_registry_access(args: argparse.Namespace, owner_open_id: str | None, metadata: dict, user_open_id: str | None) -> None:
    mode = metadata.get("mode", "personal")
    if mode == "team":
        if not args.team:
            raise SystemExit("Team registry requires explicit --team for write operations.")
        allowed = [str(item) for item in metadata.get("allowed_user_open_ids", []) if str(item)]
        if allowed and user_open_id and user_open_id not in allowed and not args.allow_foreign_registry:
            raise SystemExit("Authorized Feishu user is not listed in the team registry allowed users.")
        return
    if mode != "personal":
        raise SystemExit("Registry mode must be 'personal' or 'team'.")
    if owner_open_id and user_open_id and owner_open_id != user_open_id and not args.allow_foreign_registry:
        raise SystemExit(
            "Registry owner does not match the authorized Feishu user. "
            "Use your own registry path via --registry or LARK_WORKLOG_REGISTRY, "
            "or pass --allow-foreign-registry intentionally."
        )


def save_registry(path: str, docs: dict[str, str], owner_open_id: str | None = None, metadata: dict | None = None) -> bool:
    path = ensure_parent_dir(path)
    payload = {
        "schema_version": 1,
        "owner_open_id": owner_open_id,
        "title_template": "MM-YYYY 工作记录",
        "date_heading_template": "MM-DD-YYYY",
        "docs": dict(sorted(docs.items())),
    }
    if metadata:
        payload.update(metadata)
    old = None
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8-sig") as handle:
            old = handle.read()
    new = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if old == new:
        return False
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(new)
    return True


def cache_scope(registry_path: str) -> str:
    absolute = os.path.abspath(os.path.expanduser(registry_path))
    return hashlib.sha256(absolute.encode("utf-8")).hexdigest()[:16]


def load_json_file(path: str, fallback):
    path = expanded_path(path)
    if not os.path.exists(path):
        return fallback
    try:
        with open(path, "r", encoding="utf-8-sig") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError):
        return fallback


def save_json_file(path: str, payload) -> None:
    path = ensure_parent_dir(path)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def cached_doc(cache_path: str, registry_path: str, key: str, title: str) -> str | None:
    payload = load_json_file(cache_path, {})
    if not isinstance(payload, dict):
        return None
    entry = payload.get(cache_scope(registry_path), {}).get(key)
    if not isinstance(entry, dict) or entry.get("title") != title:
        return None
    doc = entry.get("doc")
    return str(doc) if doc else None


def remember_doc_cache(cache_path: str, registry_path: str, key: str, title: str, doc: str, revision_id: int | None = None) -> None:
    payload = load_json_file(cache_path, {})
    if not isinstance(payload, dict):
        payload = {}
    scope = cache_scope(registry_path)
    payload.setdefault(scope, {})
    payload[scope][key] = {
        "doc": doc,
        "title": title,
        "revision_id": revision_id,
        "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
    }
    try:
        save_json_file(cache_path, payload)
    except OSError as exc:
        if RUN_LARK_VERBOSE:
            print_redacted(f"Warning: skipped local cache update for {cache_path}: {exc}", file=sys.stderr)


def read_failed_queue(path: str) -> list[dict]:
    path = expanded_path(path)
    if not os.path.exists(path):
        return []
    entries: list[dict] = []
    with open(path, "r", encoding="utf-8-sig") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(entry, dict):
                entries.append(entry)
    return entries


def write_failed_queue(path: str, entries: list[dict]) -> None:
    path = ensure_parent_dir(path)
    with open(path, "w", encoding="utf-8") as handle:
        for entry in entries:
            handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")


def failed_queue_items(path: str, registry_path: str, date: str) -> list[str]:
    scope = cache_scope(registry_path)
    result: list[str] = []
    for entry in read_failed_queue(path):
        if entry.get("scope") != scope or entry.get("date") != date:
            continue
        items = entry.get("items", [])
        if isinstance(items, list):
            result.extend(str(item) for item in items if str(item).strip())
    return dedupe(result)


def append_failed_queue(path: str, registry_path: str, date: str, title: str, items: list[str], reason: str) -> None:
    if not items:
        return
    entries = read_failed_queue(path)
    entry = {
        "scope": cache_scope(registry_path),
        "date": date,
        "title": title,
        "items": dedupe(items),
        "reason": compact_error(reason),
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
    }
    entries.append(entry)
    write_failed_queue(path, entries)


def remove_failed_queue_date(path: str, registry_path: str, date: str) -> bool:
    entries = read_failed_queue(path)
    scope = cache_scope(registry_path)
    remaining = [entry for entry in entries if not (entry.get("scope") == scope and entry.get("date") == date)]
    if len(remaining) == len(entries):
        return False
    write_failed_queue(path, remaining)
    return True


def read_optional_items(args: argparse.Namespace) -> list[str]:
    try:
        return read_items(args)
    except SystemExit as exc:
        if str(exc).startswith("No archive items provided"):
            return []
        raise


def print_group_preview(title: str, date: str, items: list[str]) -> None:
    clean_items = [item for item in items if not is_internal_note_item(item)]
    groups = group_items(clean_items)
    print(f"Preview: {title} / {date}")
    print(f"New items: {len(clean_items)}")
    for category in ordered_categories(groups):
        subgroups = groups[category]
        if not any(values for values in subgroups.values()):
            continue
        print(f"- {category}")
        for subcategory in ordered_subcategories(subgroups):
            values = subgroups[subcategory]
            if not values:
                continue
            print(f"  - {subcategory}")
            for item in values:
                print(f"    - {canonical_item(item)}")


def print_repair_notes(notes: list[str], limit: int = 12) -> None:
    if not notes:
        print("Repair report: no structural notes.")
        return
    print(f"Repair report: {len(notes)} note(s)")
    for note in notes[:limit]:
        print(f"- {note}")
    if len(notes) > limit:
        print(f"- ... {len(notes) - limit} more")


def check_doc_readable(doc: str) -> tuple[bool, str]:
    proc = run_lark(
        [
            "docs",
            "+fetch",
            "--api-version",
            "v2",
            "--as",
            "user",
            "--doc",
            doc,
            "--doc-format",
            "markdown",
        ],
        check=False,
    )
    if proc.returncode != 0:
        return False, compact_error(proc.stderr or proc.stdout or "fetch failed")
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return False, "fetch returned non-JSON output"
    document = payload.get("data", {}).get("document", {}) if isinstance(payload, dict) else {}
    revision = document.get("revision_id", "unknown")
    return True, f"readable; revision {revision}"


def run_doctor(args: argparse.Namespace, archive_day: dt.date) -> int:
    checks: list[tuple[str, str, str, str | None]] = []

    def add(status: str, name: str, detail: str, fix: str | None = None) -> None:
        checks.append((status, name, detail, fix))

    lark_path = lark_cli_command()
    if lark_path:
        add("ok", "lark-cli", lark_path)
    else:
        add("fail", "lark-cli", "not found", "npx @larksuite/cli@latest install")

    payload: dict | None = None
    user_open_id: str | None = None
    if lark_path:
        payload, auth_error = auth_status_payload()
        if payload:
            user_open_id, user_error = authorized_user_open_id(payload)
            if user_open_id:
                add("ok", "auth", "authorized user")
            else:
                add(
                    "fail",
                    "auth",
                    user_error or "not authorized",
                    auth_fix_hint(user_error),
                )
        else:
            add(
                "fail",
                "auth",
                auth_error or "not authorized",
                auth_fix_hint(auth_error),
            )

    docs: dict[str, str] = {}
    owner_open_id: str | None = None
    metadata: dict = {}
    registry_path = expanded_path(args.registry)
    if os.path.exists(registry_path):
        try:
            docs, owner_open_id = load_registry(args.registry)
            metadata = load_registry_metadata(args.registry)
            add("ok", "registry", args.registry)
        except (OSError, json.JSONDecodeError) as exc:
            add("fail", "registry", compact_error(str(exc)), "replace it with a valid monthly-docs JSON file")
    else:
        add("warn", "registry", "not found", f"{sys.argv[0]} --init --registry {args.registry}")

    mode = metadata.get("mode", "personal")
    if mode == "team":
        add("ok", "registry mode", "team; write commands require explicit --team")
        allowed = [str(item) for item in metadata.get("allowed_user_open_ids", []) if str(item)]
        if allowed and user_open_id and user_open_id not in allowed:
            add("fail", "team access", "authorized user is not listed in allowed users")
    elif mode != "personal":
        add("fail", "registry mode", "must be personal or team")
    elif owner_open_id and user_open_id and owner_open_id != user_open_id:
        add("fail", "registry owner", "authorized user does not match registry owner", "use your own registry or pass --allow-foreign-registry intentionally")
    elif owner_open_id:
        add("ok", "registry owner", "matches authorized user" if user_open_id else "stored")

    key = month_key(archive_day)
    doc = docs.get(key)
    if doc and payload:
        readable, detail = check_doc_readable(doc)
        add("ok" if readable else "fail", "current month", f"{document_title(archive_day, metadata)} {detail}")
    elif doc:
        add("warn", "current month", f"{document_title(archive_day, metadata)} configured; auth not checked")
    else:
        add("warn", "current month", f"{document_title(archive_day, metadata)} not in registry", f"{sys.argv[0]} --init")

    for status, name, detail, fix in checks:
        print(f"[{status}] {name}: {detail}")
        if fix:
            print(f"  fix: {fix}")
    return 1 if any(status == "fail" for status, _, _, _ in checks) else 0


def archive_worklog(args: argparse.Namespace, archive_day: dt.date, archive_date: str, items: list[str]) -> ArchiveResult:
    docs, owner_open_id = load_registry(args.registry)
    metadata = load_registry_metadata(args.registry)
    user_open_id = current_user_open_id()
    if args.team:
        metadata = normalized_registry_metadata(args, metadata, user_open_id)
    ensure_registry_access(args, owner_open_id, metadata, user_open_id)
    items = sign_team_items(items, metadata, author_name(args, metadata))
    title = document_title(archive_day, metadata)
    key = month_key(archive_day)
    doc = args.doc or docs.get(key)
    if not doc and not args.no_cache:
        doc = cached_doc(args.cache, args.registry, key, title)
        if doc and args.verbose:
            print(f"Using cached monthly document for {title}", file=sys.stderr)
    if not doc and not args.no_search_existing:
        doc = find_doc_by_title(title)
        if doc and args.verbose:
            print(f"Found existing monthly document: {title}", file=sys.stderr)

    written_items: list[str] = []
    cached_revision_id: int | None = None
    with month_lock(key, enabled=not args.no_lock):
        for attempt in range(1, args.retries + 1):
            current, revision_id = fetch_doc(doc) if doc else ("", -1)
            cached_revision_id = revision_id if revision_id >= 0 else cached_revision_id
            existing_section = dict(split_sections(current)).get(archive_date, "")
            existing_groups = normalize_section_groups(existing_section)
            existing_items = {
                canonical_item(item)
                for subgroups in existing_groups.values()
                for sub_items in subgroups.values()
                for item in sub_items
            }
            unique_items = [item for item in items if canonical_item(item) not in existing_items]
            written_items = list(unique_items)
            if not unique_items and not args.normalize_only:
                if doc and (not args.doc or args.register_doc):
                    docs[key] = doc
                    save_registry(args.registry, docs, owner_open_id or user_open_id, metadata)
                    if not args.no_cache:
                        remember_doc_cache(args.cache, args.registry, key, title, doc, cached_revision_id)
                return ArchiveResult(doc or "", title, archive_date, 0)
            merged = merge_document(current, archive_date, unique_items)
            if args.dry_run:
                print(merged, end="")
                if not doc:
                    print(f"\n[dry-run] would create monthly document: {title}", file=sys.stderr)
                return ArchiveResult(doc or "", title, archive_date, len(unique_items), dry_run=True)
            if args.normalize_only and not doc:
                raise SystemExit("No monthly document found to normalize.")
            if args.existing_only and not doc:
                raise SystemExit(
                    f"No existing monthly worklog found for {title}. "
                    "Run --init --existing-only after registering an existing document, or rerun without --existing-only to create one."
                )
            current_sections = split_sections(current)
            has_prefix_content = any(section_date is None and section.strip() for section_date, section in current_sections)
            same_day_top = bool(current_sections and current_sections[0][0] == archive_date)
            if not doc:
                doc = create_doc(title, markdown_to_xml(merged, title))
                break
            if doc and same_day_top and existing_section and not has_prefix_content and not args.force_overwrite:
                merged_section = dict(split_sections(merged)).get(archive_date, "")
                fallback_merged = merged
                if (
                    section_replace_args_are_safe(existing_section, merged_section)
                    and not markdown_section_replace_is_risky(existing_section)
                    and not markdown_section_replace_is_risky(merged_section)
                    and update_section(doc, existing_section, merged_section, revision_id)
                ):
                    latest, latest_revision_id = fetch_doc(doc)
                    latest_section = dict(split_sections(latest)).get(archive_date, "")
                    if section_signature(latest_section) == section_signature(merged_section):
                        cached_revision_id = latest_revision_id
                        break
                    if update_doc(doc, markdown_to_xml(fallback_merged, title), latest_revision_id, title=title):
                        break
            if not existing_section and not has_prefix_content and not args.force_overwrite:
                xml_content, xml_revision = fetch_doc_xml(doc)
                title_id = find_title_id(xml_content)
                new_groups = group_items(unique_items)
                if title_id and insert_after_block(doc, title_id, day_section_to_xml(archive_date, new_groups), xml_revision):
                    break
            if update_doc(doc, markdown_to_xml(merged, title), revision_id, title=title):
                break
            if attempt == args.retries:
                raise SystemExit("Update failed after revision-conflict retries.")
            time.sleep(0.5 * attempt)
        if not args.doc or args.register_doc:
            docs[key] = doc
            save_registry(args.registry, docs, owner_open_id or user_open_id, metadata)
        if written_items:
            cached_revision_id = verify_items(doc, archive_date, written_items)
        if doc and not args.no_cache:
            remember_doc_cache(args.cache, args.registry, key, title, doc, cached_revision_id)
    return ArchiveResult(doc or "", title, archive_date, len(written_items))


def repair_worklog(args: argparse.Namespace, archive_day: dt.date, archive_date: str) -> RepairResult:
    docs, owner_open_id = load_registry(args.registry)
    metadata = load_registry_metadata(args.registry)
    user_open_id = current_user_open_id()
    ensure_registry_access(args, owner_open_id, metadata, user_open_id)
    title = document_title(archive_day, metadata)
    key = month_key(archive_day)
    doc = args.doc or docs.get(key)
    if not doc:
        raise SystemExit("No monthly document found to repair. Run --init first or pass --doc.")

    with month_lock(key, enabled=not args.no_lock):
        current, revision_id = fetch_doc(doc)
        if args.all_dates:
            normalized = normalize_document_sections(current)
            dates = [section_date for section_date, _ in split_sections(current) if section_date]
            notes = repair_notes(current)
            if args.dry_run:
                print(normalized, end="")
                print_repair_notes(notes)
                return RepairResult(doc, title, dates, normalized.strip() != current.strip(), dry_run=True)
            if normalized.strip() == strip_non_date_title(current).strip():
                print_repair_notes(notes)
                if not args.no_cache:
                    remember_doc_cache(args.cache, args.registry, key, title, doc, revision_id)
                return RepairResult(doc, title, dates, False)
            if not update_doc(doc, markdown_to_xml(normalized, title), revision_id, title=title):
                raise SystemExit("Repair failed during full-document rewrite.")
            latest, latest_revision_id = fetch_doc(doc)
            latest_sections = dict(split_sections(latest))
            expected_sections = dict(split_sections(normalized))
            for section_date in dates:
                if section_signature(latest_sections.get(section_date, "")) != section_signature(expected_sections.get(section_date, "")):
                    raise SystemExit(f"Repair verification failed for {section_date}.")
            print_repair_notes(notes)
            if not args.no_cache:
                remember_doc_cache(args.cache, args.registry, key, title, doc, latest_revision_id)
            return RepairResult(doc, title, dates, True)

        sections = dict(split_sections(current))
        existing_section = sections.get(archive_date)
        if existing_section is None:
            raise SystemExit(f"No section found for {archive_date}. Use --all-dates to repair the whole month.")
        normalized_section = normalize_date_section(archive_date, existing_section)
        notes = repair_notes(current, archive_date)
        if args.dry_run:
            print(normalized_section + "\n")
            print_repair_notes(notes)
            return RepairResult(doc, title, [archive_date], normalized_section.strip() != existing_section.strip(), dry_run=True)
        if normalized_section.strip() == existing_section.strip():
            print_repair_notes(notes)
            if not args.no_cache:
                remember_doc_cache(args.cache, args.registry, key, title, doc, revision_id)
            return RepairResult(doc, title, [archive_date], False)
        repaired_document = replace_document_section(current, archive_date, normalized_section)
        if not update_doc(doc, markdown_to_xml(repaired_document, title), revision_id, title=title):
            raise SystemExit("Repair failed during full-document rewrite.")
        latest, latest_revision_id = fetch_doc(doc)
        repaired = dict(split_sections(latest)).get(archive_date, "")
        if section_signature(repaired) != section_signature(normalized_section):
            raise SystemExit(f"Repair verification failed for {archive_date}.")
        print_repair_notes(notes)
        if not args.no_cache:
            remember_doc_cache(args.cache, args.registry, key, title, doc, latest_revision_id)
        return RepairResult(doc, title, [archive_date], True)


def run_init(args: argparse.Namespace, archive_day: dt.date, archive_date: str) -> int:
    items = read_optional_items(args)
    if items:
        args.register_doc = True
        result = archive_worklog(args, archive_day, archive_date, items)
        print_archive_result(args, result)
        print(f"Registry: {args.registry}")
        return 0

    user_open_id = current_user_open_id()
    if not user_open_id:
        raise SystemExit(
            "lark-cli user auth is not ready. "
            'Run: lark-cli auth login --recommend --domain docs,drive,markdown --scope "search:docs:read"'
        )
    docs, owner_open_id = load_registry(args.registry)
    metadata = normalized_registry_metadata(args, load_registry_metadata(args.registry), user_open_id)
    ensure_registry_access(args, owner_open_id, metadata, user_open_id)

    key = month_key(archive_day)
    title = document_title(archive_day, metadata)
    doc = args.doc or docs.get(key)
    action = "Registered"
    with month_lock(key, enabled=not args.no_lock):
        if not doc and not args.no_search_existing:
            doc = find_doc_by_title(title)
        if not doc:
            if args.existing_only:
                raise SystemExit(
                    f"No existing monthly worklog found for {title}. "
                    "Pass --doc to register a known document, or rerun --init without --existing-only to create one."
                )
            doc = create_doc(title, markdown_to_xml("", title))
            action = "Created"
        docs[key] = doc
        save_registry(args.registry, docs, owner_open_id or user_open_id, metadata)
        if not args.no_cache:
            remember_doc_cache(args.cache, args.registry, key, title, doc)
    print(f"{action} worklog {title} in registry {args.registry}.")
    if args.print_doc:
        print(f"Document: {doc}")
    return 0


def print_archive_result(args: argparse.Namespace, result: ArchiveResult) -> None:
    if result.dry_run:
        return
    if result.item_count == 0 and not args.normalize_only:
        print(f"No new worklog items for {result.date}.")
    elif args.normalize_only and result.item_count == 0:
        print(f"Normalized worklog {result.title} for {result.date}.")
    else:
        print(f"Updated worklog {result.title} for {result.date} with {result.item_count} item(s).")
    if args.print_doc and result.doc:
        print(f"Document: {result.doc}")


def print_repair_result(args: argparse.Namespace, result: RepairResult) -> None:
    if result.dry_run:
        return
    scope = "all dates" if args.all_dates else ", ".join(result.dates)
    if result.changed:
        print(f"Repaired worklog {result.title} for {scope}.")
    else:
        print(f"No repair changes needed for {result.title} / {scope}.")
    if args.print_doc and result.doc:
        print(f"Document: {result.doc}")


def main() -> int:
    global RUN_LARK_VERBOSE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--doc", default=os.environ.get("LARK_WORKLOG_DOC"))
    parser.add_argument("--registry", default=default_registry_path())
    parser.add_argument("--cache", default=default_cache_path(), help="Local cache path for month-to-document lookups.")
    parser.add_argument("--no-cache", action="store_true", help="Do not read or write the local document lookup cache.")
    parser.add_argument("--failed-queue", default=default_failed_queue_path(), help="Local JSONL queue for failed archive items.")
    parser.add_argument("--queue-failed", action="store_true", help="If archiving fails, save submitted items to the local failed queue.")
    parser.add_argument("--no-replay-failed", action="store_true", help="Do not automatically replay queued failed items for the same date.")
    parser.add_argument("--date", default=None, help="Archive date, YYYY-MM-DD or MM-DD-YYYY. Defaults to today.")
    parser.add_argument("--tz", default=os.environ.get("LARK_WORKLOG_TZ", "Asia/Shanghai"))
    parser.add_argument("--item", action="append", help="Worklog bullet item. Repeat as needed.")
    parser.add_argument("--content", help="Newline-separated bullet items.")
    parser.add_argument("--preview", action="store_true", help="Print a short structural preview without touching Feishu.")
    parser.add_argument("--doctor", action="store_true", help="Check local lark-cli, auth, registry, and current month readiness.")
    parser.add_argument("--init", action="store_true", help="Create or register the current monthly document in the local registry.")
    parser.add_argument("--structure-only", action="store_true", help="Print parsed item structure and exit. Unstructured items fall back to Other / work content.")
    parser.add_argument("--classify-only", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--dry-run", action="store_true", help="Print the merged Markdown only. Use --preview for a short output.")
    parser.add_argument("--no-lock", action="store_true", help="Disable local month lock.")
    parser.add_argument("--no-search-existing", action="store_true", help="Do not search Feishu for an existing monthly doc before creating.")
    parser.add_argument("--existing-only", action="store_true", help="Use only an existing monthly document; never create a new one.")
    parser.add_argument("--register-doc", action="store_true", help="Save --doc as this month's registry entry after a successful update.")
    parser.add_argument("--force-overwrite", action="store_true", help="Rewrite the monthly document instead of same-day section replace or new-day block insert.")
    parser.add_argument("--normalize-only", action="store_true", help="Rewrite the current monthly document into the normalized list structure without requiring new items.")
    parser.add_argument("--all-dates", action="store_true", help="With --normalize-only, repair every dated section in the monthly document.")
    parser.add_argument("--team", action="store_true", help="Explicitly opt into a team shared worklog registry for init/write/repair.")
    parser.add_argument("--team-id", help="Team identifier stored in a team registry. Required when creating one.")
    parser.add_argument("--author", default=os.environ.get("LARK_WORKLOG_AUTHOR"), help="Author display name for team work-content attribution.")
    parser.add_argument("--allow-user-open-id", action="append", help="Allowed user OpenID for a team registry. Repeat as needed; kept only in the local registry.")
    parser.add_argument("--share-policy", help="Human-readable team sharing policy stored in the local registry, such as manual or workspace.")
    parser.add_argument("--title-prefix", help="Optional title prefix for team monthly documents.")
    parser.add_argument("--allow-foreign-registry", action="store_true", help="Allow using a registry owned by a different Feishu user.")
    parser.add_argument("--verbose", action="store_true", help="Print extra operational messages without dumping document content.")
    parser.add_argument("--print-doc", action="store_true", help="Print the full document locator after a successful init or archive.")
    parser.add_argument("--retries", type=int, default=3, help="Retry on revision conflicts.")
    args = parser.parse_args()
    RUN_LARK_VERBOSE = bool(args.verbose or os.environ.get("LARK_WORKLOG_VERBOSE"))

    archive_day = parse_date(args.date) if args.date else today(args.tz)
    archive_date = display_date(archive_day)

    if args.doctor:
        return run_doctor(args, archive_day)

    if args.init:
        return run_init(args, archive_day, archive_date)

    if args.normalize_only:
        result = repair_worklog(args, archive_day, archive_date)
        print_repair_result(args, result)
        return 0

    items = read_items(args)
    preview_metadata = load_registry_metadata(args.registry)
    if args.team:
        preview_metadata = normalized_registry_metadata(args, preview_metadata, None)
    if args.preview:
        preview_items = sign_team_items(items, preview_metadata, author_name(args, preview_metadata))
        print_group_preview(document_title(archive_day, preview_metadata), archive_date, preview_items)
        return 0
    if args.structure_only or args.classify_only:
        preview_items = sign_team_items(items, preview_metadata, author_name(args, preview_metadata))
        for item in preview_items:
            category, subcategory, text = split_category_prefix(item)
            final_category = category or categorize_item(text)
            final_subcategory = subcategory or subcategorize_item(text)
            print(f"{final_category} :: {final_subcategory} :: {canonical_item(text)}")
        return 0

    queued_items: list[str] = []
    if not args.no_replay_failed:
        queued_items = failed_queue_items(args.failed_queue, args.registry, archive_date)
        if queued_items:
            items = dedupe([*queued_items, *items])
            if args.verbose:
                print(f"Replaying {len(queued_items)} queued failed item(s) for {archive_date}.", file=sys.stderr)

    try:
        result = archive_worklog(args, archive_day, archive_date, items)
    except SystemExit as exc:
        if args.queue_failed:
            append_failed_queue(args.failed_queue, args.registry, archive_date, document_title(archive_day, preview_metadata), items, str(exc))
            print(f"Queued failed worklog item(s) for {archive_date}: {args.failed_queue}", file=sys.stderr)
        raise
    if queued_items and not result.dry_run:
        remove_failed_queue_date(args.failed_queue, args.registry, archive_date)
    print_archive_result(args, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

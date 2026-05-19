#!/usr/bin/env python3
"""Archive daily work bullets into monthly Feishu/Lark worklog documents."""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import html
import json
import os
import re
import subprocess
import sys
import time
from contextlib import contextmanager
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape as xml_escape
from zoneinfo import ZoneInfo


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
PRIVATE_REGISTRY = os.path.join(SKILL_DIR, "references", "monthly-docs.local.json")
DEFAULT_REGISTRY = os.path.join(os.path.expanduser("~"), ".config", "lark-worklog-archive", "monthly-docs.json")
DATE_HEADING = re.compile(r"(?m)^#{1,6} ((?:\d{4}-\d{2}-\d{2})|(?:\d{2}-\d{2}-\d{4}))\s*$")
INTERNAL_NOTE_ITEMS = {
    "今日通过 Codex/Agent 完成的工作",
    "后续记录格式",
    "每天记录：目标、使用 Agent 完成的开发内容、关键命令/文件、验证结果、遗留问题。",
    "同类内容合并到分类 bullet 下，具体工作作为二级无序列表记录。",
    "约定每一天使用一级标题 `# YYYY-MM-DD`，标题下只写无序列表，不再使用二级标题或小节标题。",
}
CATEGORY_ORDER = [
    "飞书 CLI / 工作记录",
    "Ubuntu 环境",
    "n3mapping",
    "RL 环境",
    "其他",
]
SUBCATEGORY_ORDER = [
    "工作内容",
    "验证与测试",
    "问题与风险",
    "开发环境",
    "代码与仓库",
    "其他",
]
CATEGORY_RULES = [
    (
        "飞书 CLI / 工作记录",
        (
            "飞书",
            "feishu",
            "lark",
            "lark-cli",
            "工作记录",
            "归档",
            "月度",
            "registry",
            "monthly-docs",
            "skill",
            "文档",
            "多对话",
            "跨对话",
            "多机",
            "跨 pc",
            "同日",
            "revision",
            "fetch/merge/retry",
            "dry-run",
            "分类",
            "二级列表",
        ),
    ),
    (
        "n3mapping",
        (
            "n3mapping",
            "ros_wrapper",
            "humble",
            "noetic",
            "colcon",
            "catkin",
            "rviz",
            "save_map",
            "optimization.log",
            "ros2",
            "ros1",
        ),
    ),
    (
        "RL 环境",
        (
            "rl",
            "robot_lab",
            "go2w",
            "isaac",
            "isaac sim",
            "isaac lab",
            "seanav",
            "sea-nav",
            "him",
            "unitree",
            "applauncher",
            "venv",
            "虚拟环境",
            "迁移包",
            "多地形",
            "训练",
        ),
    ),
    (
        "Ubuntu 环境",
        (
            "ubuntu",
            "bash",
            "bashrc",
            "proxy",
            "代理",
            "rtk",
            "codex",
            "claude code",
            "gemini cli",
            "终端",
        ),
    ),
]
SUBCATEGORY_RULES = [
    ("验证与测试", ("验证", "测试", "dry-run", "py_compile", "skill is valid")),
    ("问题与风险", ("风险", "问题", "失败", "冲突", "修复", "漏洞")),
    ("开发环境", ("rtk", "proxy", "bashrc", "环境", "安装", "授权", "配置")),
    ("代码与仓库", ("脚本", "代码", "仓库", "git", "commit", "push", "repo", "github")),
]


def default_registry_path() -> str:
    if os.environ.get("LARK_WORKLOG_REGISTRY"):
        return os.environ["LARK_WORKLOG_REGISTRY"]
    if os.path.exists(PRIVATE_REGISTRY):
        return PRIVATE_REGISTRY
    return DEFAULT_REGISTRY


def run_lark(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.setdefault("LARK_CLI_NO_PROXY", "1")
    proc = subprocess.run(
        ["lark-cli", *args],
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and proc.returncode != 0:
        if proc.stderr:
            print(proc.stderr, file=sys.stderr, end="")
        if proc.stdout:
            print(proc.stdout, file=sys.stderr, end="")
        raise SystemExit(proc.returncode)
    if check and proc.stderr:
        print(proc.stderr, file=sys.stderr, end="")
    return proc


@contextmanager
def month_lock(key: str, enabled: bool = True):
    if not enabled:
        yield
        return
    path = os.path.join("/tmp", f"lark-worklog-archive-{key}.lock")
    with open(path, "w", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def today(tz_name: str) -> dt.date:
    return dt.datetime.now(ZoneInfo(tz_name)).date()


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


def split_category_prefix(item: str) -> tuple[str | None, str | None, str]:
    text = strip_item_marker(item)
    if "::" in text:
        parts = [part.strip() for part in text.split("::") if part.strip()]
        if len(parts) >= 3:
            return parts[0], parts[1], "::".join(parts[2:]).strip()
        if len(parts) == 2:
            if parts[0] in CATEGORY_ORDER:
                return parts[0], None, parts[1]
            if parts[0] in SUBCATEGORY_ORDER:
                return None, parts[0], parts[1]
            return parts[0], None, parts[1]
    if "：" in text:
        category, content = text.split("：", 1)
        category = category.strip()
        content = content.strip()
        if category in CATEGORY_ORDER and content:
            return category, None, content
        if category in SUBCATEGORY_ORDER and content:
            return None, category, content
    return None, None, text


def categorize_item(item: str) -> str:
    explicit, _, text = split_category_prefix(item)
    if explicit:
        return explicit
    lowered = text.lower()
    for category, keywords in CATEGORY_RULES:
        if any(keyword.lower() in lowered for keyword in keywords):
            return category
    return "其他"


def subcategorize_item(item: str) -> str:
    _, explicit, text = split_category_prefix(item)
    if explicit:
        return explicit
    lowered = text.lower()
    for category, keywords in SUBCATEGORY_RULES:
        if any(keyword.lower() in lowered for keyword in keywords):
            return category
    return "工作内容"


def canonical_item(item: str) -> str:
    _, _, text = split_category_prefix(item)
    for escaped, plain in (("\\`", "`"), ("\\<", "<"), ("\\>", ">"), ("\\[", "["), ("\\]", "]")):
        text = text.replace(escaped, plain)
    return text.strip()


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
                elif text in SUBCATEGORY_ORDER and text not in CATEGORY_ORDER:
                    current_category = None
                    current_subcategory = text
                else:
                    current_category = text if text in CATEGORY_ORDER else categorize_item(text)
                    current_subcategory = None
                    groups.setdefault(current_category, {})
            elif level == 1 and has_child:
                if current_category:
                    current_subcategory = text if text in SUBCATEGORY_ORDER else subcategorize_item(text)
                    groups[current_category].setdefault(current_subcategory, [])
                else:
                    current_subcategory = text if text in SUBCATEGORY_ORDER else subcategorize_item(text)
            else:
                category, subcategory, content = split_category_prefix(text)
                if level == 0:
                    target_category = category or categorize_item(content)
                    target_subcategory = subcategory or subcategorize_item(content)
                elif current_category and current_subcategory and level > 1:
                    guessed_category = category or categorize_item(content)
                    target_category = guessed_category if guessed_category != "其他" else current_category
                    target_subcategory = current_subcategory
                elif current_category:
                    guessed_category = category or categorize_item(content)
                    target_category = guessed_category if guessed_category != "其他" else current_category
                    target_subcategory = subcategory or subcategorize_item(content)
                elif current_subcategory:
                    target_category = category or categorize_item(content)
                    target_subcategory = current_subcategory
                else:
                    target_category = category or categorize_item(content)
                    target_subcategory = subcategory or subcategorize_item(content)
                add_group_item(groups, target_category, target_subcategory, content)
                if level == 0:
                    current_category = None
                    current_subcategory = None
            index += 1
            continue
        add_group_item(groups, categorize_item(stripped), subcategorize_item(stripped), stripped)
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
    new_groups = merge_groups(group_items(clean_new_items), old_groups)
    new_section = render_day_section(date, new_groups)
    parts = [new_section, *remaining]
    return "\n\n".join(part for part in parts if part).strip() + "\n"


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
                item_xml = "".join(f"<li>{xml_escape(canonical_item(item))}</li>" for item in items)
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
    return document.get("content", ""), int(document.get("revision_id", -1))


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
    return None


def find_doc_by_title(title: str) -> str | None:
    proc = run_lark(
        [
            "docs",
            "+search",
            "--as",
            "user",
            "--query",
            f'intitle:"{title}"',
            "--filter",
            '{"only_title":true,"doc_types":["DOC","DOCX"]}',
            "--page-size",
            "10",
        ],
        check=False,
    )
    if proc.returncode != 0:
        return None
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None
    for item in iter_dicts(payload):
        candidate_title = item.get("title") or item.get("name") or item.get("title_highlighted")
        if not isinstance(candidate_title, str) or strip_tags(candidate_title) != title:
            continue
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
        print(proc.stderr, file=sys.stderr, end="")
    if proc.stdout:
        print(proc.stdout, file=sys.stderr, end="")
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
            item_xml = "".join(f"<li>{xml_escape(canonical_item(item))}</li>" for item in items)
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


def verify_items(doc: str, date: str, items: list[str]) -> None:
    content, _ = fetch_doc(doc)
    sections = dict(split_sections(content))
    section = sections.get(date, "")
    section_groups = normalize_section_groups(section)
    section_items = {
        canonical_item(item)
        for subgroups in section_groups.values()
        for items in subgroups.values()
        for item in items
    }
    missing = [item for item in items if canonical_item(item) not in section_items]
    if missing:
        raise SystemExit(f"Verification failed; missing archived item(s): {missing}")


def current_user_open_id() -> str | None:
    proc = run_lark(["auth", "status"], check=False)
    if proc.returncode != 0:
        return None
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None
    value = payload.get("userOpenId")
    return str(value) if value else None


def load_registry(path: str) -> tuple[dict[str, str], str | None]:
    if not os.path.exists(path):
        return {}, None
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    docs = payload.get("docs", payload)
    owner = payload.get("owner_open_id")
    return {str(key): str(value) for key, value in docs.items()}, str(owner) if owner else None


def save_registry(path: str, docs: dict[str, str], owner_open_id: str | None = None) -> bool:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = {
        "owner_open_id": owner_open_id,
        "title_template": "MM-YYYY 工作记录",
        "date_heading_template": "MM-DD-YYYY",
        "docs": dict(sorted(docs.items())),
    }
    old = None
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as handle:
            old = handle.read()
    new = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if old == new:
        return False
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(new)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--doc", default=os.environ.get("LARK_WORKLOG_DOC"))
    parser.add_argument("--registry", default=default_registry_path())
    parser.add_argument("--date", default=None, help="Archive date, YYYY-MM-DD or MM-DD-YYYY. Defaults to today.")
    parser.add_argument("--tz", default=os.environ.get("LARK_WORKLOG_TZ", "Asia/Shanghai"))
    parser.add_argument("--item", action="append", help="Worklog bullet item. Repeat as needed.")
    parser.add_argument("--content", help="Newline-separated bullet items.")
    parser.add_argument("--dry-run", action="store_true", help="Print the merged Markdown only.")
    parser.add_argument("--no-lock", action="store_true", help="Disable local month lock.")
    parser.add_argument("--no-search-existing", action="store_true", help="Do not search Feishu for an existing monthly doc before creating.")
    parser.add_argument("--register-doc", action="store_true", help="Save --doc as this month's registry entry after a successful update.")
    parser.add_argument("--force-overwrite", action="store_true", help="Always rewrite the monthly document instead of same-day block insertion.")
    parser.add_argument("--normalize-only", action="store_true", help="Rewrite the current monthly document into the normalized list structure without requiring new items.")
    parser.add_argument("--allow-foreign-registry", action="store_true", help="Allow using a registry owned by a different Feishu user.")
    parser.add_argument("--retries", type=int, default=3, help="Retry on revision conflicts.")
    args = parser.parse_args()

    archive_day = parse_date(args.date) if args.date else today(args.tz)
    archive_date = display_date(archive_day)
    items = [] if args.normalize_only and not args.item and args.content is None else read_items(args)
    docs, owner_open_id = load_registry(args.registry)
    user_open_id = current_user_open_id()
    if owner_open_id and user_open_id and owner_open_id != user_open_id and not args.allow_foreign_registry:
        raise SystemExit(
            "Registry owner does not match the authorized Feishu user. "
            "Use your own registry path via --registry or LARK_WORKLOG_REGISTRY, "
            "or pass --allow-foreign-registry intentionally."
        )
    key = month_key(archive_day)
    doc = args.doc or docs.get(key)
    if not doc and not args.no_search_existing:
        doc = find_doc_by_title(month_title(archive_day))
        if doc:
            print(f"Found existing monthly document: {doc}", file=sys.stderr)

    with month_lock(key, enabled=not args.no_lock):
        for attempt in range(1, args.retries + 1):
            current, revision_id = fetch_doc(doc) if doc else ("", -1)
            existing_section = dict(split_sections(current)).get(archive_date, "")
            existing_groups = normalize_section_groups(existing_section)
            existing_items = {
                canonical_item(item)
                for subgroups in existing_groups.values()
                for items in subgroups.values()
                for item in items
            }
            unique_items = [item for item in items if canonical_item(item) not in existing_items]
            if not unique_items and not args.normalize_only:
                print(f"No new worklog items for {archive_date}.")
                return 0
            merged = merge_document(current, archive_date, unique_items)
            if args.dry_run:
                print(merged, end="")
                if not doc:
                    print(f"\n[dry-run] would create monthly document: {month_title(archive_day)}", file=sys.stderr)
                return 0
            if args.normalize_only and not doc:
                raise SystemExit("No monthly document found to normalize.")
            same_day_top = bool(split_sections(current) and split_sections(current)[0][0] == archive_date)
            if doc and same_day_top and not args.force_overwrite:
                # Same-day grouping changes the current day section; use a section-level replace
                # to keep category buckets coherent without rewriting the whole document.
                merged_section = dict(split_sections(merged)).get(archive_date, "")
                if existing_section and update_section(doc, existing_section, merged_section, revision_id):
                    break
            if not doc:
                doc = create_doc(month_title(archive_day), markdown_to_xml(merged, month_title(archive_day)))
                break
            if not existing_section:
                xml_content, xml_revision = fetch_doc_xml(doc)
                title_id = find_title_id(xml_content)
                new_groups = group_items(unique_items)
                if title_id and insert_after_block(doc, title_id, day_section_to_xml(archive_date, new_groups), xml_revision):
                    break
            if update_doc(doc, markdown_to_xml(merged, month_title(archive_day)), revision_id, title=month_title(archive_day)):
                break
            if attempt == args.retries:
                raise SystemExit("Update failed after revision-conflict retries.")
            time.sleep(0.5 * attempt)
        if not args.doc or args.register_doc:
            docs[key] = doc
            save_registry(args.registry, docs, owner_open_id or user_open_id)
        if unique_items:
            verify_items(doc, archive_date, unique_items)
    print(f"Updated worklog {doc} for {archive_date} with {len(unique_items)} item(s).")
    print(f"Monthly document: {month_title(archive_day)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET


SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parents[1]
SCRIPT_PATH = SKILL_DIR / "scripts" / "archive_worklog.py"


def load_archive_module():
    spec = importlib.util.spec_from_file_location("archive_worklog_under_test", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FakeLark:
    def __init__(self, markdown: str, xml: str | None = None, user_open_id: str = "ou_test"):
        self.doc = "doc-test"
        self.markdown = markdown
        self.xml = xml or '<title id="title-1">05-2026 工作记录</title>'
        self.user_open_id = user_open_id
        self.revision = 1
        self.calls: list[list[str]] = []

    def __call__(self, args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
        self.calls.append(list(args))
        if args == ["auth", "status"]:
            return self.completed(args, {"userOpenId": self.user_open_id})
        if args[:2] == ["docs", "+fetch"]:
            content = self.xml if "--detail" in args else self.markdown
            return self.completed(args, {"data": {"document": {"content": content, "revision_id": self.revision}}})
        if args[:2] == ["docs", "+create"]:
            content = value_after(args, "--content")
            self.markdown = xml_day_section_to_markdown(content)
            self.revision += 1
            return self.completed(args, {"data": {"document": {"url": self.doc, "revision_id": self.revision}}})
        if args[:2] == ["docs", "+update"]:
            command = value_after(args, "--command")
            if command == "str_replace":
                pattern = value_after(args, "--pattern")
                content = value_after(args, "--content")
                if pattern not in self.markdown:
                    return subprocess.CompletedProcess(["lark-cli", *args], 1, "", "pattern not found")
                self.markdown = self.markdown.replace(pattern, content, 1)
            elif command == "block_insert_after":
                content_xml = value_after(args, "--content")
                inserted = xml_day_section_to_markdown(content_xml)
                self.markdown = "\n\n".join(part for part in (inserted, self.markdown.strip()) if part)
            elif command == "overwrite":
                self.markdown = value_after(args, "--content")
            else:
                return subprocess.CompletedProcess(["lark-cli", *args], 1, "", f"unsupported command {command}")
            self.revision += 1
            return self.completed(args, {"data": {"document": {"revision_id": self.revision}}})
        return subprocess.CompletedProcess(["lark-cli", *args], 1, "", f"unexpected lark args: {args}")

    @staticmethod
    def completed(args: list[str], payload: dict) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(["lark-cli", *args], 0, json.dumps(payload), "")

    def commands(self) -> list[str]:
        result: list[str] = []
        for args in self.calls:
            if "--command" in args:
                result.append(value_after(args, "--command"))
        return result


def value_after(args: list[str], flag: str) -> str:
    return args[args.index(flag) + 1]


def xml_day_section_to_markdown(content_xml: str) -> str:
    root = ET.fromstring(f"<root>{content_xml}</root>")
    lines: list[str] = []
    h1 = root.find("h1")
    if h1 is not None and h1.text:
        lines.extend([f"# {h1.text.strip()}", ""])
    ul = root.find("ul")
    if ul is not None:
        lines.extend(xml_list_to_markdown(ul, 0))
    return "\n".join(lines).strip()


def xml_list_to_markdown(ul: ET.Element, level: int) -> list[str]:
    lines: list[str] = []
    for li in ul.findall("li"):
        text = (li.text or "").strip()
        if text:
            lines.append(f"{'  ' * level}- {text}")
        child = li.find("ul")
        if child is not None:
            lines.extend(xml_list_to_markdown(child, level + 1))
    return lines


@contextlib.contextmanager
def argv(*args: str):
    old = sys.argv
    sys.argv = ["archive_worklog.py", "--no-cache", "--no-replay-failed", *args]
    try:
        yield
    finally:
        sys.argv = old


class ArchiveWorklogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load_archive_module()

    def test_date_and_section_normalization(self) -> None:
        sections = self.mod.split_sections("# 2026-05-20\n\n- new\n\n# 05-19-2026\n\n- old")
        self.assertEqual([date for date, _ in sections], ["05-20-2026", "05-19-2026"])

    def test_grouping_and_legacy_domain_migration(self) -> None:
        section = """# 05-19-2026

- 验证与测试
  - 清理旧迁移遗留的未知分类，确认跨对话并发保护内容归入飞书 CLI 分类。
- 开发环境
  - 安装并配置 RTK，用于 Codex、Claude Code、Gemini CLI 的命令输出压缩与 token 节省。
- 其他
  - 工作内容
    - 整理 Go2W RL 工作区，建立 /home/user/rl_ws/go2w_rl 作为新的统一工作区。
"""
        groups = self.mod.normalize_section_groups(section)
        self.assertIn("飞书 CLI / 工作记录", groups)
        self.assertIn("Ubuntu 环境", groups)
        self.assertIn("RL 环境", groups)
        self.assertEqual(
            self.flatten(groups["飞书 CLI / 工作记录"]["验证与测试"]),
            ["清理旧迁移遗留的未知分类，确认跨对话并发保护内容归入飞书 CLI 分类。"],
        )
        self.assertEqual(
            self.flatten(groups["Ubuntu 环境"]["开发环境"]),
            ["安装并配置 RTK，用于 Codex、Claude Code、Gemini CLI 的命令输出压缩与 token 节省。"],
        )

    def test_merge_document_appends_same_subcategory_after_existing_items(self) -> None:
        current = """# 05-19-2026

- 飞书 CLI / 工作记录
  - 工作内容
    - 创建 lark-worklog-archive Skill。
"""
        merged = self.mod.merge_document(
            current,
            "05-19-2026",
            ["飞书 CLI / 工作记录::工作内容::安装到全局 Codex skills。"],
        )
        self.assertLess(merged.index("创建 lark-worklog-archive Skill。"), merged.index("安装到全局 Codex skills。"))

    def test_markdown_to_xml_preserves_nested_lists(self) -> None:
        markdown = """# 05-19-2026

- 飞书 CLI / 工作记录
  - 工作内容
    - 创建 Skill。
  - 验证与测试
    - Skill 校验通过。
"""
        xml = self.mod.markdown_to_xml(markdown, "05-2026 工作记录")
        self.assertIn("<li>飞书 CLI / 工作记录<ul>", xml)
        self.assertIn("<li>工作内容<ul><li>创建 Skill。</li></ul></li>", xml)
        self.assertIn("<li>验证与测试<ul><li>Skill 校验通过。</li></ul></li>", xml)

    def test_main_same_day_uses_section_replace_and_verifies(self) -> None:
        fake = FakeLark(
            """# 05-19-2026

- 飞书 CLI / 工作记录
  - 工作内容
    - 创建 lark-worklog-archive Skill。
"""
        )
        self.mod.run_lark = fake
        with tempfile.TemporaryDirectory() as tempdir:
            with argv(
                "--doc",
                fake.doc,
                "--registry",
                str(Path(tempdir) / "registry.json"),
                "--no-lock",
                "--date",
                "2026-05-19",
                "--item",
                "飞书 CLI / 工作记录::工作内容::安装到全局 Codex skills。",
            ):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(self.mod.main(), 0)
        self.assertIn("str_replace", fake.commands())
        self.assertIn("Updated worklog 05-2026 工作记录 for 05-19-2026 with 1 item(s).", output.getvalue())
        self.assertNotIn(fake.doc, output.getvalue())
        self.assertLess(fake.markdown.index("创建 lark-worklog-archive Skill。"), fake.markdown.index("安装到全局 Codex skills。"))

    def test_main_new_day_uses_block_insert_after(self) -> None:
        fake = FakeLark("# 05-19-2026\n\n- Ubuntu 环境\n  - 开发环境\n    - 配置代理。")
        self.mod.run_lark = fake
        with tempfile.TemporaryDirectory() as tempdir:
            with argv(
                "--doc",
                fake.doc,
                "--registry",
                str(Path(tempdir) / "registry.json"),
                "--no-lock",
                "--date",
                "2026-05-20",
                "--item",
                "飞书 CLI / 工作记录::工作内容::继续完善归档 Skill。",
            ):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(self.mod.main(), 0)
        self.assertIn("block_insert_after", fake.commands())
        self.assertTrue(fake.markdown.startswith("# 05-20-2026"))
        self.assertIn("继续完善归档 Skill。", fake.markdown)

    def test_custom_category_rules_can_be_loaded_from_json(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            rules = Path(tempdir) / "category-rules.json"
            rules.write_text(
                json.dumps(
                    {
                        "category_order": ["Custom 域", "其他"],
                        "subcategory_order": ["Review", "工作内容"],
                        "fallback_category": "其他",
                        "fallback_subcategory": "工作内容",
                        "category_rules": [{"name": "Custom 域", "keywords": ["alpha"]}],
                        "subcategory_rules": [{"name": "Review", "keywords": ["check"]}],
                    }
                ),
                encoding="utf-8",
            )
            self.mod.apply_category_config(self.mod.load_category_config(str(rules)))
        self.assertEqual(self.mod.categorize_item("alpha task"), "Custom 域")
        self.assertEqual(self.mod.subcategorize_item("check result"), "Review")
        self.assertEqual(self.mod.categorize_item("unmatched"), "其他")
        self.assertEqual(self.mod.subcategorize_item("unmatched"), "工作内容")
        rendered = self.mod.merge_document("", "05-20-2026", ["alpha check result"])
        self.assertIn("- Custom 域\n  - Review\n    - alpha check result", rendered)

    def test_classify_only_does_not_call_lark(self) -> None:
        def fail_lark(args, check=True):
            raise AssertionError(f"lark-cli should not be called: {args}")

        self.mod.run_lark = fail_lark
        with argv("--classify-only", "--item", "验证 n3mapping Humble launch smoke。"):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(self.mod.main(), 0)
        self.assertIn("n3mapping :: 验证与测试 :: 验证 n3mapping Humble launch smoke。", output.getvalue())

    def test_preview_does_not_call_lark_and_prints_short_grouping(self) -> None:
        def fail_lark(args, check=True):
            raise AssertionError(f"lark-cli should not be called: {args}")

        self.mod.run_lark = fail_lark
        with argv(
            "--preview",
            "--date",
            "2026-05-20",
            "--item",
            "飞书 CLI / 工作记录::代码与仓库::新增 doctor/init/preview 入口。",
        ):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(self.mod.main(), 0)
        text = output.getvalue()
        self.assertIn("Preview: 05-2026 工作记录 / 05-20-2026", text)
        self.assertIn("- 飞书 CLI / 工作记录\n  - 代码与仓库\n    - 新增 doctor/init/preview 入口。", text)

    def test_doctor_checks_registry_without_printing_doc_locator(self) -> None:
        fake = FakeLark("# 05-20-2026\n\n- 飞书 CLI / 工作记录\n  - 工作内容\n    - existing")
        self.mod.run_lark = fake
        self.mod.shutil.which = lambda command: f"/usr/bin/{command}"
        with tempfile.TemporaryDirectory() as tempdir:
            registry = Path(tempdir) / "registry.json"
            registry.write_text(
                json.dumps({"schema_version": 1, "owner_open_id": "ou_test", "docs": {"2026-05": fake.doc}}),
                encoding="utf-8",
            )
            with argv("--doctor", "--registry", str(registry), "--date", "2026-05-20"):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(self.mod.main(), 0)
        text = output.getvalue()
        self.assertIn("[ok] current month: 05-2026 工作记录 readable; revision 1", text)
        self.assertNotIn(fake.doc, text)

    def test_init_creates_monthly_doc_and_schema_versioned_registry(self) -> None:
        fake = FakeLark("")
        self.mod.run_lark = fake
        with tempfile.TemporaryDirectory() as tempdir:
            registry = Path(tempdir) / "registry.json"
            with argv(
                "--init",
                "--registry",
                str(registry),
                "--no-lock",
                "--no-search-existing",
                "--date",
                "2026-05-20",
            ):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(self.mod.main(), 0)
            payload = json.loads(registry.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["docs"]["2026-05"], fake.doc)
        self.assertIn("Created worklog 05-2026 工作记录", output.getvalue())
        self.assertNotIn(fake.doc, output.getvalue())

    def test_team_init_requires_explicit_metadata_and_stores_allowed_user(self) -> None:
        fake = FakeLark("")
        self.mod.run_lark = fake
        with tempfile.TemporaryDirectory() as tempdir:
            registry = Path(tempdir) / "registry.json"
            with argv(
                "--init",
                "--team",
                "--team-id",
                "shared-dev",
                "--title-prefix",
                "Shared Dev",
                "--registry",
                str(registry),
                "--no-lock",
                "--no-search-existing",
                "--date",
                "2026-05-20",
            ):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(self.mod.main(), 0)
            payload = json.loads(registry.read_text(encoding="utf-8"))
        self.assertEqual(payload["mode"], "team")
        self.assertEqual(payload["team_id"], "shared-dev")
        self.assertEqual(payload["doc_title_prefix"], "Shared Dev")
        self.assertIn("ou_test", payload["allowed_user_open_ids"])
        self.assertIn("Shared Dev 05-2026 工作记录", output.getvalue())

    def test_team_registry_blocks_writes_without_explicit_team_flag(self) -> None:
        fake = FakeLark("# 05-20-2026\n\n- old")
        self.mod.run_lark = fake
        with tempfile.TemporaryDirectory() as tempdir:
            registry = Path(tempdir) / "registry.json"
            registry.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "mode": "team",
                        "team_id": "shared-dev",
                        "allowed_user_open_ids": ["ou_test"],
                        "docs": {"2026-05": fake.doc},
                    }
                ),
                encoding="utf-8",
            )
            with argv("--registry", str(registry), "--no-lock", "--date", "2026-05-20", "--item", "测试。"):
                with self.assertRaises(SystemExit) as raised:
                    self.mod.main()
        self.assertIn("Team registry requires explicit --team", str(raised.exception))
        self.assertEqual(fake.commands(), [])

    def test_normalize_only_specific_date_uses_section_replace(self) -> None:
        fake = FakeLark(
            """# 05-20-2026

- 验证与测试
  - 清理旧迁移遗留的未知分类，确认跨对话并发保护内容归入飞书 CLI 分类。

# 05-19-2026

- Ubuntu 环境
  - 开发环境
    - 配置代理。
"""
        )
        self.mod.run_lark = fake
        with tempfile.TemporaryDirectory() as tempdir:
            with argv(
                "--doc",
                fake.doc,
                "--registry",
                str(Path(tempdir) / "registry.json"),
                "--no-lock",
                "--normalize-only",
                "--date",
                "2026-05-20",
            ):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(self.mod.main(), 0)
        self.assertIn("str_replace", fake.commands())
        self.assertNotIn("overwrite", fake.commands())
        self.assertIn("moved top-level subcategory '验证与测试'", output.getvalue())
        self.assertIn("- 飞书 CLI / 工作记录\n  - 验证与测试", fake.markdown)

    def test_normalize_only_all_dates_uses_overwrite_and_report(self) -> None:
        fake = FakeLark(
            """# 05-20-2026

- 验证与测试
  - 清理旧迁移遗留的未知分类，确认跨对话并发保护内容归入飞书 CLI 分类。

# 05-19-2026

- 开发环境
  - 安装并配置 RTK。
"""
        )
        self.mod.run_lark = fake
        with tempfile.TemporaryDirectory() as tempdir:
            with argv(
                "--doc",
                fake.doc,
                "--registry",
                str(Path(tempdir) / "registry.json"),
                "--no-lock",
                "--normalize-only",
                "--all-dates",
                "--date",
                "2026-05-20",
            ):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(self.mod.main(), 0)
        self.assertIn("overwrite", fake.commands())
        self.assertIn("Repair report:", output.getvalue())
        self.assertIn("Repaired worklog 05-2026 工作记录 for all dates.", output.getvalue())

    def test_old_flat_registry_schema_still_loads(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            registry = Path(tempdir) / "registry.json"
            registry.write_text(json.dumps({"2026-05": "doc-old", "title_template": "legacy"}), encoding="utf-8")
            docs, owner = self.mod.load_registry(str(registry))
        self.assertEqual(docs, {"2026-05": "doc-old"})
        self.assertIsNone(owner)

    def test_doc_cache_is_scoped_by_registry_and_title(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            cache = str(Path(tempdir) / "cache.json")
            registry = str(Path(tempdir) / "registry.json")
            other_registry = str(Path(tempdir) / "other.json")
            self.mod.remember_doc_cache(cache, registry, "2026-05", "05-2026 工作记录", "doc-a", 7)
            self.assertEqual(self.mod.cached_doc(cache, registry, "2026-05", "05-2026 工作记录"), "doc-a")
            self.assertIsNone(self.mod.cached_doc(cache, registry, "2026-05", "06-2026 工作记录"))
            self.assertIsNone(self.mod.cached_doc(cache, other_registry, "2026-05", "05-2026 工作记录"))

    def test_failed_queue_round_trip_and_remove_by_date(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            queue = str(Path(tempdir) / "failed.jsonl")
            registry = str(Path(tempdir) / "registry.json")
            self.mod.append_failed_queue(queue, registry, "05-20-2026", "05-2026 工作记录", ["- A", "- A", "- B"], "failed")
            self.mod.append_failed_queue(queue, registry, "05-19-2026", "05-2026 工作记录", ["- old"], "failed")
            self.assertEqual(self.mod.failed_queue_items(queue, registry, "05-20-2026"), ["- A", "- B"])
            self.assertTrue(self.mod.remove_failed_queue_date(queue, registry, "05-20-2026"))
            self.assertEqual(self.mod.failed_queue_items(queue, registry, "05-20-2026"), [])
            self.assertEqual(self.mod.failed_queue_items(queue, registry, "05-19-2026"), ["- old"])

    def test_registry_owner_guard_blocks_foreign_registry(self) -> None:
        fake = FakeLark("# 05-19-2026\n\n- old")
        self.mod.run_lark = fake
        with tempfile.TemporaryDirectory() as tempdir:
            registry = Path(tempdir) / "registry.json"
            registry.write_text(
                json.dumps({"owner_open_id": "ou_other", "docs": {"2026-05": fake.doc}}),
                encoding="utf-8",
            )
            with argv("--registry", str(registry), "--no-lock", "--item", "测试。"):
                with self.assertRaises(SystemExit) as raised:
                    self.mod.main()
        self.assertIn("Registry owner does not match", str(raised.exception))
        self.assertEqual(fake.commands(), [])

    def test_public_files_do_not_contain_private_lark_values(self) -> None:
        forbidden = [
            re.compile(r"https?://\S*(?:feishu|larksuite)\S*"),
            re.compile(r"\bou_[0-9a-f]{16,}\b"),
            re.compile(r"\bcli_[a-f0-9]{12,}\b"),
        ]
        paths = [path for path in (REPO_ROOT / "README.md", REPO_ROOT / ".gitignore") if path.exists()]
        paths.extend(path for path in SKILL_DIR.rglob("*") if path.is_file())
        violations: list[str] = []
        for path in paths:
            relative = path.relative_to(REPO_ROOT)
            if "__pycache__" in relative.parts or relative.name.endswith(".pyc"):
                continue
            if relative.as_posix().endswith("monthly-docs.local.json"):
                continue
            text = path.read_text(encoding="utf-8")
            for pattern in forbidden:
                if pattern.search(text):
                    violations.append(str(relative))
        self.assertEqual(violations, [])

    @staticmethod
    def flatten(items: list[str]) -> list[str]:
        return [item[2:].strip() if item.startswith("- ") else item.strip() for item in items]


if __name__ == "__main__":
    unittest.main()

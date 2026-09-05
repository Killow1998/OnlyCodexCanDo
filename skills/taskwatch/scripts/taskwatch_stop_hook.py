#!/usr/bin/env python3
"""Codex Stop hook for TaskWatch goal-terminal email notifications."""

from __future__ import annotations

from datetime import datetime, timezone
from collections import deque
from dataclasses import dataclass, field
import hashlib
import json
import os
import re
import smtplib
import ssl
import subprocess
import sys
from email.message import EmailMessage
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


CODEX_HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
ENV_PATH = CODEX_HOME / "taskwatch.env"
STATE_DIR = CODEX_HOME / "taskwatch-state"
AUDIT_LOG_PATH = STATE_DIR / "taskwatch-hook-audit.log"
AUDIT_LOG_MAX_BYTES = 1024 * 1024
REQUIRED_KEYS = ("SMTP_HOST", "SMTP_PORT", "SMTP_SECURITY", "SMTP_USER", "SMTP_PASS", "EMAIL_FROM", "EMAIL_TO")
TERMINAL_STATUSES = {"complete", "blocked", "usageLimited"}
DISPLAY_TZ = ZoneInfo("Asia/Shanghai")
DEFAULT_SMTP_TIMEOUT_SECONDS = 5.0
TERMINAL_EVENT_MAX_AGE_SECONDS = 10 * 60
USAGE_LIMIT_MARKERS = (
    "You've hit your usage limit",
    "Visit https://chatgpt.com/codex/settings/usage",
)
ARCHIVE_ATTEMPT_MARKERS = (
    "archive_worklog.py",
    "lark-worklog-archive",
    "今日归档",
    "今天归档",
    "同步到飞书工作记录",
)
ARCHIVE_SUCCESS_MARKERS = (
    "Updated worklog ",
    "已记录到飞书",
    "Monthly document:",
)
ARCHIVE_FAILURE_MARKERS = (
    "Verification failed",
    "need_user_authorization",
    "Repair failed",
    "archive failed",
)
TEST_SIGNAL_PATTERNS = (
    ("pytest", re.compile(r"\bpytest\b.*\b(pass|passed|fail|failed|error|errors)\b|\b(pass|passed|fail|failed|error|errors)\b.*\bpytest\b", re.I)),
    ("unittest", re.compile(r"\bunittest\b|Ran \d+ tests? in .*\b(OK|FAILED)\b", re.I)),
    ("colcon test", re.compile(r"\bcolcon test\b|test result:.*\b(failures?|errors?)\b", re.I)),
    ("cargo test", re.compile(r"\bcargo test\b|test result:.*\b(ok|FAILED)\b", re.I)),
    ("npm test", re.compile(r"\bnpm test\b|\btest(s)?\b.*\b(pass|passed|fail|failed)\b", re.I)),
    ("build", re.compile(r"\bbuild (succeeded|failed)\b|\b(successfully built|build error)\b", re.I)),
    ("check", re.compile(r"\bcheck\.py\b.*\b(ok|pass|passed|fail|failed)\b|\bSkill is valid\b", re.I)),
)


@dataclass
class TranscriptFacts:
    latest_goal_event: dict[str, Any] | None = None
    started_at: datetime | None = None
    last_assistant_text: str = ""
    recent_text_chunks: deque[str] = field(default_factory=lambda: deque(maxlen=80))
    archive_attempted: bool = False
    archive_success: str = ""
    archive_failure: str = ""
    raw_tail: str = ""


def ensure_private_state_dir(path: Path | None = None) -> None:
    path = path or STATE_DIR
    path.mkdir(parents=True, mode=0o700, exist_ok=True)
    path.chmod(0o700)


def audit_event(action: str, **fields: Any) -> None:
    try:
        ensure_private_state_dir()
        if AUDIT_LOG_PATH.exists() and AUDIT_LOG_PATH.stat().st_size > AUDIT_LOG_MAX_BYTES:
            rotated_path = AUDIT_LOG_PATH.with_suffix(AUDIT_LOG_PATH.suffix + ".1")
            if rotated_path.exists():
                rotated_path.unlink()
            AUDIT_LOG_PATH.replace(rotated_path)
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "pid": os.getpid(),
        }
        for key, value in fields.items():
            if isinstance(value, Path):
                record[key] = str(value)
            elif isinstance(value, (str, int, float, bool)) or value is None:
                record[key] = value
            else:
                record[key] = str(value)
        with AUDIT_LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=True, sort_keys=True) + "\n")
        AUDIT_LOG_PATH.chmod(0o600)
    except Exception:
        return


def _load_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        raise FileNotFoundError(path)
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"invalid env line: {raw_line!r}")
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def load_email_config(path: Path = ENV_PATH) -> dict[str, str]:
    config = _load_env_file(path)
    if config.get("MAIL_TRANSPORT") == "agent-mail":
        import agent_mail
        agent_mail.validate(config)
        return config
    missing = [key for key in REQUIRED_KEYS if not config.get(key)]
    if missing:
        raise ValueError("missing email config keys: " + ", ".join(missing))
    return config


def send_email(config: dict[str, str], subject: str, body: str) -> None:
    if config.get("MAIL_TRANSPORT") == "agent-mail":
        import agent_mail
        agent_mail.send(config, subject, body)
        return
    smtp_port = int(config["SMTP_PORT"])
    security = config["SMTP_SECURITY"].strip().lower()
    smtp_timeout = float(config.get("SMTP_TIMEOUT_SECONDS") or DEFAULT_SMTP_TIMEOUT_SECONDS)

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = config["EMAIL_FROM"]
    message["To"] = config["EMAIL_TO"]
    message.set_content(body, subtype="plain", charset="utf-8")

    if security == "ssl":
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(config["SMTP_HOST"], smtp_port, timeout=smtp_timeout, context=context) as smtp:
            smtp.login(config["SMTP_USER"], config["SMTP_PASS"])
            smtp.send_message(message)
        return

    context = ssl.create_default_context()
    with smtplib.SMTP(config["SMTP_HOST"], smtp_port, timeout=smtp_timeout) as smtp:
        smtp.ehlo()
        if security == "starttls":
            smtp.starttls(context=context)
            smtp.ehlo()
        smtp.login(config["SMTP_USER"], config["SMTP_PASS"])
        smtp.send_message(message)


def find_transcript_path(payload: dict[str, Any]) -> Path | None:
    transcript_path = payload.get("transcript_path")
    if transcript_path:
        path = Path(transcript_path).expanduser()
        if path.exists():
            return path

    session_id = payload.get("session_id")
    if not session_id:
        return None
    sessions_dir = CODEX_HOME / "sessions"
    candidates = sorted(sessions_dir.rglob("*.jsonl"))
    filename_matches = [
        path
        for path in candidates
        if path.stem == session_id or path.stem.endswith("-" + str(session_id))
    ]
    if len(filename_matches) == 1:
        return filename_matches[0]
    exact_meta_matches: list[Path] = []
    for path in candidates:
        try:
            with path.open("r", encoding="utf-8", errors="replace") as handle:
                for raw_line in handle:
                    try:
                        item = json.loads(raw_line)
                    except json.JSONDecodeError:
                        continue
                    if item.get("type") == "session_meta" and str((item.get("payload") or {}).get("id", "")) == str(session_id):
                        exact_meta_matches.append(path)
                        break
        except OSError:
            continue
    return exact_meta_matches[0] if len(exact_meta_matches) == 1 else None


def parse_thread_goal_state_item(item: dict[str, Any]) -> dict[str, Any] | None:
    if item.get("type") != "event_msg":
        return None
    payload = item.get("payload") or {}
    if payload.get("type") != "thread_goal_updated":
        return None
    goal = payload.get("goal") or {}
    status = goal.get("status")
    if not isinstance(status, str):
        return None
    return {
        "status": status,
        "objective": goal.get("objective", ""),
        "turn_id": payload.get("turnId", ""),
        "created_at": goal.get("createdAt", ""),
        "updated_at": goal.get("updatedAt", ""),
        "time_used_seconds": goal.get("timeUsedSeconds", ""),
        "timestamp": item.get("timestamp", ""),
        "source": "thread_goal_updated",
    }


def parse_goal_event_item(item: dict[str, Any]) -> dict[str, Any] | None:
    state = parse_thread_goal_state_item(item)
    return state if state is not None and state["status"] in TERMINAL_STATUSES else None


def parse_goal_event(raw_line: str) -> dict[str, Any] | None:
    try:
        item = json.loads(raw_line)
    except json.JSONDecodeError:
        return None
    return parse_goal_event_item(item) if isinstance(item, dict) else None


def parse_update_goal_state_item(item: dict[str, Any]) -> dict[str, Any] | None:
    if item.get("type") != "response_item":
        return None
    payload = item.get("payload") or {}
    if payload.get("type") != "function_call_output":
        return None
    output = payload.get("output")
    if not isinstance(output, str):
        return None
    try:
        result = json.loads(output)
    except json.JSONDecodeError:
        return None
    goal = result.get("goal") if isinstance(result, dict) else None
    if not isinstance(goal, dict):
        return None
    status = goal.get("status")
    if not isinstance(status, str):
        return None
    return {
        "status": status,
        "objective": goal.get("objective", ""),
        "turn_id": payload.get("turnId", ""),
        "created_at": goal.get("createdAt", ""),
        "updated_at": goal.get("updatedAt", ""),
        "time_used_seconds": goal.get("timeUsedSeconds", ""),
        "timestamp": item.get("timestamp", ""),
        "source": "update_goal",
    }


def parse_update_goal_output_item(item: dict[str, Any]) -> dict[str, Any] | None:
    state = parse_update_goal_state_item(item)
    return state if state is not None and state["status"] in TERMINAL_STATUSES else None


def parse_update_goal_output(raw_line: str) -> dict[str, Any] | None:
    try:
        item = json.loads(raw_line)
    except json.JSONDecodeError:
        return None
    return parse_update_goal_output_item(item) if isinstance(item, dict) else None


def event_is_fresh(event: dict[str, Any], now: datetime | None = None) -> bool:
    if now is None:
        return True
    event_time = parse_timestamp(event.get("updated_at")) or parse_timestamp(event.get("timestamp"))
    if event_time is None:
        return True
    # Only notify for recent terminal events; old transcript state can be re-read on every Stop hook.
    return abs((now - event_time).total_seconds()) <= TERMINAL_EVENT_MAX_AGE_SECONDS


def scan_transcript(transcript_path: Path) -> TranscriptFacts:
    facts = TranscriptFacts()
    with transcript_path.open("r", encoding="utf-8", errors="replace") as handle:
        for raw_line in handle:
            facts.raw_tail = (facts.raw_tail + raw_line)[-4000:]
            try:
                item = json.loads(raw_line)
            except json.JSONDecodeError:
                continue
            if not isinstance(item, dict):
                continue
            goal_state = parse_thread_goal_state_item(item) or parse_update_goal_state_item(item)
            if goal_state is not None:
                facts.latest_goal_event = goal_state if goal_state["status"] in TERMINAL_STATUSES else None
            if facts.started_at is None:
                facts.started_at = parse_timestamp(item.get("timestamp"))
            payload = item.get("payload") or {}
            fragments = extract_text_fragments(payload)
            if fragments:
                facts.recent_text_chunks.append("\n".join(fragments)[-4000:])
            if item.get("type") == "response_item" and payload.get("type") == "message" and payload.get("role") == "assistant":
                assistant_fragments = extract_text_fragments(payload.get("content"))
                if assistant_fragments:
                    facts.last_assistant_text = "\n".join(assistant_fragments)[-16000:]
            if item.get("type") != "response_item" or payload.get("type") != "function_call_output":
                continue
            for fragment in extract_text_fragments(payload.get("output")):
                if not fragment.strip():
                    continue
                source = normalize_text(fragment, limit=800)
                if is_noise_fragment(source):
                    continue
                lower = source.lower()
                if any(marker.lower() in lower for marker in ARCHIVE_ATTEMPT_MARKERS):
                    facts.archive_attempted = True
                if not facts.archive_success and any(marker.lower() in lower for marker in ARCHIVE_SUCCESS_MARKERS):
                    facts.archive_success = source
                if not facts.archive_failure and any(marker.lower() in lower for marker in ARCHIVE_FAILURE_MARKERS):
                    facts.archive_failure = source
    return facts


def detect_terminal_event(
    transcript_path: Path,
    last_assistant_message: str | None = None,
    now: datetime | None = None,
    facts: TranscriptFacts | None = None,
) -> dict[str, Any] | None:
    facts = facts or scan_transcript(transcript_path)
    latest_goal_event = facts.latest_goal_event

    if latest_goal_event is not None and event_is_fresh(latest_goal_event, now=now):
        return latest_goal_event

    fallback_text = (last_assistant_message or "") + "\n" + facts.raw_tail
    if any(marker in fallback_text for marker in USAGE_LIMIT_MARKERS):
        return {
            "status": "usageLimited",
            "objective": "",
            "turn_id": "",
            "updated_at": "",
            "timestamp": "",
            "source": "usage-limit-fallback",
        }
    return None


def state_file_for_session(state_dir: Path, session_id: str) -> Path:
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", session_id).strip("._")
    if not safe_name:
        safe_name = "session"
    if safe_name != session_id or len(safe_name) > 120:
        digest = hashlib.sha256(session_id.encode("utf-8", errors="replace")).hexdigest()[:12]
        safe_name = f"{safe_name[:80].rstrip('_') or 'session'}-{digest}"
    return state_dir / f"{safe_name}.json"


def load_sent_key(state_dir: Path, session_id: str) -> str:
    state_file = state_file_for_session(state_dir, session_id)
    if not state_file.exists():
        return ""
    try:
        payload = json.loads(state_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ""
    value = payload.get("last_sent_key")
    return value if isinstance(value, str) else ""


def store_sent_key(state_dir: Path, session_id: str, key: str) -> None:
    ensure_private_state_dir(state_dir)
    state_file = state_file_for_session(state_dir, session_id)
    state_file.write_text(json.dumps({"last_sent_key": key}, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    state_file.chmod(0o600)


def terminal_key(session_id: str, event: dict[str, Any]) -> str:
    return "|".join(
        str(part)
        for part in [
            session_id,
            event.get("status", ""),
            event.get("updated_at", ""),
            event.get("turn_id", ""),
            event.get("source", ""),
        ]
    )


def parse_timestamp(value: Any) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
    if isinstance(value, (int, float)):
        seconds = float(value)
        if abs(seconds) > 1_000_000_000_000:
            seconds /= 1000.0
        try:
            return datetime.fromtimestamp(seconds, tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def format_timestamp(value: Any) -> str:
    parsed = parse_timestamp(value)
    if parsed is None:
        return "unknown"
    local = parsed.astimezone(DISPLAY_TZ)
    return local.strftime("%Y-%m-%d %H:%M:%S") + " Asia/Shanghai"


def format_duration(start: datetime | None, end: datetime | None) -> str:
    if start is None or end is None:
        return "unknown"
    return format_duration_seconds(max(0, int((end - start).total_seconds())))


def parse_duration_seconds(value: Any) -> int | None:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return max(0, int(value))
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return max(0, int(float(text)))
        except ValueError:
            return None
    return None


def format_duration_seconds(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}秒"
    minutes, remaining_seconds = divmod(seconds, 60)
    hours, remaining_minutes = divmod(minutes, 60)
    days, remaining_hours = divmod(hours, 24)
    parts: list[str] = []
    if days:
        parts.append(f"{days}天")
    if remaining_hours:
        parts.append(f"{remaining_hours}小时")
    if remaining_minutes:
        parts.append(f"{remaining_minutes}分钟")
    if remaining_seconds and not (days or remaining_hours):
        parts.append(f"{remaining_seconds}秒")
    return "".join(parts) if parts else "0秒"


def duration_for_context(context: dict[str, Any]) -> str:
    duration_seconds = context.get("duration_seconds")
    if isinstance(duration_seconds, int):
        return format_duration_seconds(duration_seconds)
    return format_duration(context["started_at"], context["ended_at"])


def normalize_text(text: str, limit: int = 240) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def strip_markdown(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return text.replace("`", "")


def summarize_task_name(text: str, limit: int = 120) -> str:
    candidate = strip_markdown(text).strip()
    if not candidate:
        return "unknown"
    for line in candidate.splitlines():
        line = line.strip()
        if line:
            candidate = line
            break
    for separator in ("。", "；", ";"):
        if separator in candidate:
            candidate = candidate.split(separator, 1)[0].strip()
    return normalize_text(candidate, limit=limit)


def is_noise_fragment(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return True
    if stripped.startswith('{"cmd":') or stripped.startswith("{'cmd':"):
        return True
    if stripped.startswith("rg ") or stripped.startswith("grep "):
        return True
    noise_markers = ('"workdir":', '"yield_time_ms":', '"max_output_tokens":', '"cmd":')
    return any(marker in stripped for marker in noise_markers)


def clean_digest_lines(text: str, limit: int = 8) -> list[str]:
    lines: list[str] = []
    in_code = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not line:
            continue
        line = re.sub(r"^[-*+]\s+", "", line)
        line = re.sub(r"^\d+[.)]\s+", "", line)
        if is_noise_fragment(line) or line.startswith(("{", "[", "}", "]")):
            continue
        if len(line) > 300:
            continue
        lines.append(normalize_text(line, limit=180))
        if len(lines) >= limit:
            break
    if lines:
        return lines
    compact = normalize_text(text, limit=180)
    return [compact] if compact and not is_noise_fragment(compact) else []


def last_assistant_text_from_transcript(transcript_path: Path, facts: TranscriptFacts | None = None) -> str:
    return (facts or scan_transcript(transcript_path)).last_assistant_text


def extract_final_assistant_digest(
    transcript_path: Path,
    last_assistant_message: str | None,
    facts: TranscriptFacts | None = None,
) -> list[str]:
    text = (last_assistant_message or "").strip() or last_assistant_text_from_transcript(transcript_path, facts)
    return clean_digest_lines(text, limit=8)


def recent_transcript_text(
    transcript_path: Path,
    max_items: int = 80,
    facts: TranscriptFacts | None = None,
) -> str:
    collected = facts or scan_transcript(transcript_path)
    return "\n".join(list(collected.recent_text_chunks)[-max_items:])


def extract_test_signals(transcript_path: Path, facts: TranscriptFacts | None = None) -> list[str]:
    text = recent_transcript_text(transcript_path, facts=facts)
    signals: list[str] = []
    for label, pattern in TEST_SIGNAL_PATTERNS:
        if not pattern.search(text):
            continue
        status = "FAIL" if re.search(r"\b(fail|failed|failure|error|errors|FAILED)\b", text, re.I) else "PASS"
        signals.append(f"{label}: {status}")
    return signals[:5]


def run_git(cwd: str, *args: str) -> str:
    try:
        result = subprocess.run(
            ("git", "-C", cwd, *args),
            check=False,
            capture_output=True,
            text=True,
            timeout=2,
        )
    except Exception:
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def collect_git_context(cwd: str | None) -> dict[str, str]:
    if not cwd:
        return {}
    inside = run_git(cwd, "rev-parse", "--is-inside-work-tree")
    if inside != "true":
        return {}
    status_lines = [line for line in run_git(cwd, "status", "--short").splitlines() if line.strip()]
    diff_stat = run_git(cwd, "diff", "--stat", "HEAD~1..HEAD") or run_git(cwd, "diff", "--stat")
    return {
        "branch": run_git(cwd, "branch", "--show-current") or run_git(cwd, "rev-parse", "--short", "HEAD"),
        "commit": run_git(cwd, "log", "-1", "--oneline"),
        "dirty_count": str(len(status_lines)),
        "diff_stat": normalize_text(diff_stat, limit=220),
    }


def humanize_archive_detail(detail: str) -> str:
    cleaned = strip_markdown(detail).strip()
    if not cleaned or is_noise_fragment(cleaned):
        return ""
    lowered = cleaned.lower()
    if "updated worklog " in lowered or "monthly document:" in lowered or "已记录到飞书" in cleaned:
        monthly_doc = ""
        match = re.search(r"Monthly document:\s*([^\n]+)", cleaned)
        if match:
            monthly_doc = match.group(1).strip()
        if monthly_doc:
            return f"已写入飞书工作记录（{monthly_doc}）。"
        return "已写入飞书工作记录。"
    if "need_user_authorization" in lowered:
        return "归档未完成：飞书授权已失效，需要重新授权后重试。"
    if "invalid utf-8" in lowered or ".pyc" in lowered or "__pycache__" in lowered:
        return "归档未完成：归档校验扫到了缓存或二进制文件，需跳过这类文件后重试。"
    if "verification failed" in lowered:
        return "归档未完成：归档校验失败，需检查归档输出后重试。"
    if "repair failed" in lowered or "archive failed" in lowered:
        return "归档未完成：归档流程执行失败，需要检查报错后重试。"
    return normalize_text(cleaned, limit=200)


def build_result_summary(status: str, task_name: str, archive_status: str, archive_detail: str = "") -> str:
    if status == "complete":
        conclusion = "goal 已完成。"
        result = f"已完成「{task_name}」，Codex 正常收尾。"
        next_step = "无需人工介入；如需要沉淀记录，可查看归档状态和 transcript。"
    elif status == "blocked":
        conclusion = "goal 未完成，当前处于 blocked。"
        result = f"「{task_name}」被阻塞，尚未达到完成状态。"
        next_step = "需要查看阻塞原因，决定补充信息、授权、环境修复或重新运行。"
    elif status == "usageLimited":
        conclusion = "goal 未完成，Codex 使用额度已触顶。"
        result = f"「{task_name}」因额度限制中断。"
        next_step = "等待额度恢复或切换可用额度后继续。"
    else:
        conclusion = "goal 状态未知。"
        result = f"「{task_name}」已触发终态通知，但没有可识别的完成状态。"
        next_step = "需要查看 transcript 确认真实结果。"

    lines = [
        f"- 结论：{conclusion}",
        f"- 主要结果：{result}",
        f"- 归档状态：{archive_status}",
    ]
    if archive_detail:
        lines.append(f"- 归档说明：{archive_detail}")
    lines.append(f"- 后续处理：{next_step}")
    return "\n".join(lines)


def extract_text_fragments(value: Any) -> list[str]:
    fragments: list[str] = []
    if isinstance(value, str):
        fragments.append(value)
        return fragments
    if isinstance(value, list):
        for item in value:
            fragments.extend(extract_text_fragments(item))
        return fragments
    if isinstance(value, dict):
        direct = value.get("text")
        if isinstance(direct, str):
            fragments.append(direct)
        for key in ("input_text", "output_text", "message", "content", "arguments", "output"):
            if key in value:
                fragments.extend(extract_text_fragments(value[key]))
        return fragments
    return fragments


def summarize_status(status: str) -> str:
    if status == "complete":
        return "已完成，goal 正常收尾。"
    if status == "blocked":
        return "未完成，goal 已进入 blocked，需要人工处理阻塞项。"
    if status == "usageLimited":
        return "未完成，Codex 使用额度已触顶。"
    return "状态未知。"


def intervention_status(status: str) -> str:
    if status == "complete":
        return "否"
    if status == "blocked":
        return "是，需要查看阻塞原因并决定下一步。"
    if status == "usageLimited":
        return "是，需要等待额度恢复或切换可用额度后重试。"
    return "unknown"


def status_label(status: str) -> str:
    if status == "complete":
        return "DONE"
    if status == "blocked":
        return "BLOCKED"
    if status == "usageLimited":
        return "LIMITED"
    return status.upper() or "UNKNOWN"


def collect_transcript_context(
    transcript_path: Path,
    event: dict[str, Any],
    facts: TranscriptFacts | None = None,
) -> dict[str, Any]:
    facts = facts or scan_transcript(transcript_path)
    started_at = facts.started_at
    archive_attempted = facts.archive_attempted
    archive_success = facts.archive_success
    archive_failure = facts.archive_failure

    objective = summarize_task_name(str(event.get("objective", "")).strip(), limit=160)
    task_name = objective or transcript_path.stem
    goal_started_at = parse_timestamp(event.get("created_at"))
    ended_at = parse_timestamp(event.get("updated_at")) or parse_timestamp(event.get("timestamp"))
    duration_seconds = parse_duration_seconds(event.get("time_used_seconds"))
    if duration_seconds is None and goal_started_at is not None and ended_at is not None:
        duration_seconds = max(0, int((ended_at - goal_started_at).total_seconds()))
    if goal_started_at is not None:
        started_at = goal_started_at
    archive_detail = humanize_archive_detail(archive_success or archive_failure)

    if archive_success:
        archive_status = "已完成"
    elif archive_attempted and archive_failure:
        archive_status = "尝试过，但未确认成功"
    elif archive_attempted:
        archive_status = "检测到归档动作，但未确认成功"
    else:
        archive_status = "未检测到"

    return {
        "task_name": task_name or "unknown",
        "started_at": started_at,
        "ended_at": ended_at,
        "duration_seconds": duration_seconds,
        "archive_status": archive_status,
        "archive_detail": archive_detail,
    }


def build_subject(event: dict[str, Any], context: dict[str, Any]) -> str:
    task_name = summarize_task_name(str(context.get("task_name", "")).strip(), limit=48)
    status = event.get("status", "")
    if status == "complete":
        return f"[TW:DONE][{duration_for_context(context)}] {task_name}"
    if status == "blocked":
        return f"[TW:BLOCKED][NEEDS-ACTION] {task_name}"
    if status == "usageLimited":
        return f"[TW:LIMITED] {task_name}"
    return f"[TW:{status_label(str(status))}] {task_name}"


def build_body(
    payload: dict[str, Any],
    transcript_path: Path,
    event: dict[str, Any],
    context: dict[str, Any] | None = None,
    facts: TranscriptFacts | None = None,
) -> str:
    facts = facts or scan_transcript(transcript_path)
    context = context or collect_transcript_context(transcript_path, event, facts)
    started_at = context["started_at"]
    ended_at = context["ended_at"]
    duration_text = duration_for_context(context)
    subject = build_subject(event, context)
    result_summary = build_result_summary(
        event["status"],
        str(context["task_name"]),
        str(context["archive_status"]),
        str(context.get("archive_detail", "")),
    )
    final_digest = extract_final_assistant_digest(transcript_path, payload.get("last_assistant_message"), facts)
    git_context = collect_git_context(str(payload.get("cwd", "") or ""))
    test_signals = extract_test_signals(transcript_path, facts)

    lines = [
        subject,
        "",
        "一眼结论",
        f"- 状态：{status_label(event['status'])}",
        f"- 任务：{context['task_name']}",
        f"- 结果：{summarize_status(event['status'])}",
        f"- 是否需要介入：{intervention_status(event['status'])}",
        "",
        "本次产出",
    ]
    if git_context:
        lines.extend(
            [
                f"- 当前分支：{git_context.get('branch', '')}",
                f"- 最新提交：{git_context.get('commit', '')}",
                f"- 未提交文件：{git_context.get('dirty_count', '0')} 个",
            ]
        )
        if git_context.get("diff_stat"):
            lines.append(f"- diff stat：{git_context['diff_stat']}")
    else:
        lines.append("- 代码变更：未检测到 git 仓库")
    if test_signals:
        lines.append(f"- 验证：{'; '.join(test_signals)}")
    else:
        lines.append("- 验证：未检测到")
    lines.extend(
        [
            f"- 归档：{context['archive_status']}",
            f"- 耗时：{duration_text}",
            "",
            "Codex 最后结论",
        ]
    )
    if final_digest:
        lines.extend(f"- {line}" for line in final_digest)
    else:
        lines.append("- 未检测到可用的最后结论")
    lines.extend(
        [
            "",
            "后续处理",
            result_summary,
            "",
            "Debug",
            f"- session_id：{payload.get('session_id', '')}",
            f"- turn_id：{event.get('turn_id', '') or payload.get('turn_id', '')}",
            f"- cwd：{payload.get('cwd', '')}",
            f"- transcript：{transcript_path}",
            f"- event_source：{event.get('source', '')}",
            f"- started_at：{format_timestamp(started_at)}",
            f"- ended_at：{format_timestamp(ended_at)}",
        ]
    )
    if event.get("timestamp"):
        lines.append(f"- event_timestamp：{format_timestamp(event['timestamp'])}")
    if event.get("updated_at"):
        lines.append(f"- goal_updated_at：{format_timestamp(event['updated_at'])}")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        audit_event("invalid_payload", error_type=type(exc).__name__, error=str(exc))
        print(json.dumps({"continue": True}))
        print(f"taskwatch: invalid hook payload: {exc}", file=sys.stderr)
        return 0

    audit_event(
        "hook_started",
        session_id=payload.get("session_id", ""),
        cwd=payload.get("cwd", ""),
        transcript_path=payload.get("transcript_path", ""),
        has_last_assistant_message=bool(payload.get("last_assistant_message")),
    )

    transcript_path = find_transcript_path(payload)
    if transcript_path is None:
        audit_event("no_transcript", session_id=payload.get("session_id", ""))
        print(json.dumps({"continue": True}))
        return 0

    facts = scan_transcript(transcript_path)
    event = detect_terminal_event(
        transcript_path,
        payload.get("last_assistant_message"),
        now=datetime.now(timezone.utc),
        facts=facts,
    )
    if event is None:
        audit_event(
            "no_terminal_event",
            session_id=payload.get("session_id", ""),
            transcript_path=transcript_path,
        )
        print(json.dumps({"continue": True}))
        return 0

    session_id = str(payload.get("session_id", "")).strip()
    if not session_id:
        audit_event(
            "missing_session_id",
            transcript_path=transcript_path,
            status=event.get("status", ""),
            source=event.get("source", ""),
        )
        print(json.dumps({"continue": True}))
        return 0

    state_key = terminal_key(session_id, event)
    previous_state_key = load_sent_key(STATE_DIR, session_id)
    if previous_state_key == state_key:
        audit_event(
            "dedup_skip",
            session_id=session_id,
            state_key=state_key,
            status=event.get("status", ""),
            source=event.get("source", ""),
            updated_at=event.get("updated_at", ""),
        )
        print(json.dumps({"continue": True}))
        return 0

    try:
        config = load_email_config()
    except (FileNotFoundError, ValueError) as exc:
        audit_event(
            "config_error",
            session_id=session_id,
            state_key=state_key,
            error_type=type(exc).__name__,
            error=str(exc),
        )
        print(json.dumps({"continue": True}))
        return 0

    try:
        context = collect_transcript_context(transcript_path, event, facts)
        subject = build_subject(event, context)
        audit_event(
            "send_attempt",
            session_id=session_id,
            state_key=state_key,
            status=event.get("status", ""),
            source=event.get("source", ""),
            updated_at=event.get("updated_at", ""),
            subject=subject,
            smtp_host=config.get("SMTP_HOST", ""),
            email_to=config.get("EMAIL_TO", ""),
        )
        if config.get("MAIL_CONTENT") == "brief":
            body = f"TaskWatch goal: {event.get('status', 'unknown')}\nTask: {session_id}\nWorkspace: {payload.get('cwd', '')}\nEvidence: {transcript_path}\n"
        else:
            body = build_body(payload, transcript_path, event, context, facts)
        if config.get("MAIL_TRANSPORT") == "agent-mail":
            import agent_mail
            receipt = STATE_DIR / (hashlib.sha256(state_key.encode()).hexdigest() + '.delivery.json')
            if not agent_mail.send_once(config, subject, body, receipt):
                audit_event("delivery_already_claimed", session_id=session_id, receipt=receipt)
                print(json.dumps({"continue": True}))
                return 0
        else:
            send_email(config, subject, body)
        store_sent_key(STATE_DIR, session_id, state_key)
        audit_event(
            "send_success",
            session_id=session_id,
            state_key=state_key,
            status=event.get("status", ""),
            source=event.get("source", ""),
            updated_at=event.get("updated_at", ""),
            subject=subject,
            email_to=config.get("EMAIL_TO", ""),
        )
    except Exception as exc:  # pragma: no cover - defensive hook behavior
        audit_event(
            "send_failure",
            session_id=session_id,
            state_key=state_key,
            status=event.get("status", ""),
            source=event.get("source", ""),
            updated_at=event.get("updated_at", ""),
            error_type=type(exc).__name__,
            error=str(exc),
        )
        print(f"taskwatch: failed to send goal email: {exc}", file=sys.stderr)

    print(json.dumps({"continue": True}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

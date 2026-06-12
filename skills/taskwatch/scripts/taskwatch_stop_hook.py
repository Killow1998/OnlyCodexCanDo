#!/usr/bin/env python3
"""Codex Stop hook for TaskWatch goal-terminal email notifications."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
import re
import smtplib
import ssl
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


def audit_event(action: str, **fields: Any) -> None:
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
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
    missing = [key for key in REQUIRED_KEYS if not config.get(key)]
    if missing:
        raise ValueError("missing email config keys: " + ", ".join(missing))
    return config


def send_email(config: dict[str, str], subject: str, body: str) -> None:
    smtp_port = int(config["SMTP_PORT"])
    security = config["SMTP_SECURITY"].strip().lower()

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = config["EMAIL_FROM"]
    message["To"] = config["EMAIL_TO"]
    message.set_content(body, subtype="plain", charset="utf-8")

    if security == "ssl":
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(config["SMTP_HOST"], smtp_port, timeout=30, context=context) as smtp:
            smtp.login(config["SMTP_USER"], config["SMTP_PASS"])
            smtp.send_message(message)
        return

    context = ssl.create_default_context()
    with smtplib.SMTP(config["SMTP_HOST"], smtp_port, timeout=30) as smtp:
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
    matches = sorted(sessions_dir.rglob(f"*{session_id}*.jsonl"))
    return matches[-1] if matches else None


def parse_goal_event(raw_line: str) -> dict[str, Any] | None:
    try:
        item = json.loads(raw_line)
    except json.JSONDecodeError:
        return None
    if item.get("type") != "event_msg":
        return None
    payload = item.get("payload") or {}
    if payload.get("type") != "thread_goal_updated":
        return None
    goal = payload.get("goal") or {}
    status = goal.get("status")
    if status not in TERMINAL_STATUSES:
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


def parse_update_goal_output(raw_line: str) -> dict[str, Any] | None:
    try:
        item = json.loads(raw_line)
    except json.JSONDecodeError:
        return None
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
    if status not in TERMINAL_STATUSES:
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


def detect_terminal_event(transcript_path: Path, last_assistant_message: str | None = None) -> dict[str, Any] | None:
    latest_goal_event: dict[str, Any] | None = None
    transcript_text = transcript_path.read_text(encoding="utf-8", errors="replace")
    for raw_line in transcript_text.splitlines():
        event = parse_goal_event(raw_line) or parse_update_goal_output(raw_line)
        if event is not None:
            latest_goal_event = event

    if latest_goal_event is not None:
        return latest_goal_event

    fallback_text = (last_assistant_message or "") + "\n" + transcript_text[-4000:]
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
    state_dir.mkdir(parents=True, exist_ok=True)
    state_file = state_file_for_session(state_dir, session_id)
    state_file.write_text(json.dumps({"last_sent_key": key}, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


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


def collect_transcript_context(transcript_path: Path, event: dict[str, Any]) -> dict[str, Any]:
    started_at: datetime | None = None
    archive_attempted = False
    archive_success = ""
    archive_failure = ""

    for raw_line in transcript_path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            item = json.loads(raw_line)
        except json.JSONDecodeError:
            continue

        if started_at is None:
            started_at = parse_timestamp(item.get("timestamp"))

        item_type = item.get("type")
        payload = item.get("payload") or {}

        if item_type != "response_item" or payload.get("type") != "function_call_output":
            continue

        text_sources = [
            normalize_text(fragment, limit=800)
            for fragment in extract_text_fragments(payload.get("output"))
            if fragment.strip()
        ]
        for source in text_sources:
            if is_noise_fragment(source):
                continue
            lower = source.lower()
            if any(marker.lower() in lower for marker in ARCHIVE_ATTEMPT_MARKERS):
                archive_attempted = True
            if not archive_success and any(marker.lower() in lower for marker in ARCHIVE_SUCCESS_MARKERS):
                archive_success = source
            if not archive_failure and any(marker.lower() in lower for marker in ARCHIVE_FAILURE_MARKERS):
                archive_failure = source

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
    del event
    task_name = summarize_task_name(str(context.get("task_name", "")).strip(), limit=48)
    if task_name and task_name != "unknown":
        return f"goal:{task_name}"
    return "goal:unknown"


def build_body(
    payload: dict[str, Any],
    transcript_path: Path,
    event: dict[str, Any],
    context: dict[str, Any] | None = None,
) -> str:
    context = context or collect_transcript_context(transcript_path, event)
    started_at = context["started_at"]
    ended_at = context["ended_at"]
    duration_seconds = context.get("duration_seconds")
    duration_text = format_duration_seconds(duration_seconds) if isinstance(duration_seconds, int) else format_duration(started_at, ended_at)
    subject = build_subject(event, context)
    result_summary = build_result_summary(
        event["status"],
        str(context["task_name"]),
        str(context["archive_status"]),
        str(context.get("archive_detail", "")),
    )
    lines = [
        subject,
        "",
        "任务概况",
        f"- 任务是什么：{context['task_name']}",
        f"- 完成情况：{summarize_status(event['status'])}",
        f"- 是否需要介入：{intervention_status(event['status'])}",
        f"- 是否完成归档：{context['archive_status']}",
        f"- 完成时间：{format_timestamp(ended_at)}",
        f"- 花了多久：{duration_text}",
        "",
        "结果摘要",
        result_summary,
        "",
        "运行信息",
        f"- session_id：{payload.get('session_id', '')}",
        f"- turn_id：{event.get('turn_id', '') or payload.get('turn_id', '')}",
        f"- 工作目录：{payload.get('cwd', '')}",
        f"- transcript：{transcript_path}",
        f"- 事件来源：{event.get('source', '')}",
        f"- 启动时间：{format_timestamp(started_at)}",
    ]
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

    event = detect_terminal_event(transcript_path, payload.get("last_assistant_message"))
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
        context = collect_transcript_context(transcript_path, event)
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
        send_email(config, subject, build_body(payload, transcript_path, event, context))
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

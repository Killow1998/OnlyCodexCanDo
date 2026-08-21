---
name: codex-home-audit
description: Safely diagnose Codex or ChatGPT desktop startup slowness, high CPU or fan use, a very large CODEX_HOME or ~/.codex directory, excessive sessions, logs, databases, caches, plugins, or worktrees, and possible multiple-client state contention. Use for read-only size and file-count measurement, CLI-versus-desktop comparison, evidence-based cleanup planning, and pre-cleanup worktree safety checks. Never delete or move state, remove worktrees, stop processes, uninstall clients, or add antivirus exclusions without separate explicit approval.
---

# Audit Codex Home State

Diagnose the state layer before changing it. Keep measurement separate from cleanup: this Skill is read-only by default and treats transcripts, worktrees, databases, credentials, and ignored files as potentially valuable or sensitive.

## Establish the actual state owner

1. Resolve `CODEX_HOME` from the environment; otherwise use `~/.codex`.
2. Confirm the operating system, the Codex or ChatGPT desktop builds in use, the CLI version, and which clients are currently running when that information is available read-only.
3. Do not assume two clients share state merely because both exist. Verify their configuration or observed state path.
4. Keep tokens, session identifiers, transcript names, full worktree inventories, and file contents out of shared output.

Official documentation may change. Before proposing cleanup, check the current Codex troubleshooting, configuration, and worktree documentation linked from [references/cleanup-playbook.md](references/cleanup-playbook.md). Treat undocumented database ownership or regeneration claims as unverified until the current installation proves them.

## Measure before diagnosing

Run the bundled metadata-only scanner from the Skill directory:

```text
python -B scripts/audit_codex_home.py
```

Use an explicit path only when auditing a non-default or test directory:

```text
python -B scripts/audit_codex_home.py --codex-home <absolute-path> --format json
```

The scanner reads directory entries and file sizes without opening file contents. It reports aggregate top-level counts, database-like file totals, skipped links or junctions, scan errors, and immediate worktree directory count. It redacts identifier-like top-level names and stops after one million entries by default; use `--max-entries 0` only when an uncapped scan is necessary.

If the state directory is large, identify which top-level category dominates bytes and which dominates file count. A large byte total and a large file count create different startup and antivirus costs.

## Compare the smallest useful control

- Measure a lightweight CLI invocation such as `codex --version` or `codex --help` with the native timing tool, and record the exact executable and version.
- Compare that result with desktop startup observations only as a control. It can show that configuration parsing and basic CLI launch are cheap, but it does not prove which desktop subsystem is slow.
- Inspect active process and installed-version evidence when multiple clients are suspected. Do not terminate or uninstall anything during the audit.
- Check current official troubleshooting guidance for known worktree accumulation, session locations, version differences, and app restart steps.

## Classify the evidence

Use these conclusions carefully:

- **State-heavy correlation:** desktop startup is slow while the CLI control is fast and one state category has unusually high file count or size. This narrows the cause but is not process-level proof.
- **Worktree accumulation:** the audit and Git metadata show many Codex worktrees. Inspect each candidate's branch, tracked, untracked, and ignored state before removal.
- **Database or log growth:** database-like files dominate. Do not call them disposable logs until current documentation, schema inspection, or a reversible closed-client experiment establishes ownership and regeneration.
- **Multiple-client contention:** two running or installed clients are observed using the same state. Concurrent writes or scanning are a hypothesis until locks, logs, or repeatable startup behavior support it.
- **Antivirus amplification:** high file count and security-tool activity coincide. An exclusion changes security posture and is a last-resort user decision, not a default fix.

## Plan cleanup only after approval

When the user explicitly asks to clean, read [references/cleanup-playbook.md](references/cleanup-playbook.md) completely. Resolve exact absolute targets, close relevant clients, preserve recoverable backups when appropriate, and verify every Git worktree for tracked, untracked, ignored, and secret-bearing files before removal.

Never treat reinstalling as the first diagnostic step. Never recursively delete the whole Codex home. Prefer app-supported archiving, Git-native worktree management, and reversible quarantine over direct deletion.

## Report

Report:

- the resolved state path without exposing private identifiers unnecessarily;
- total bytes, files, directories, and the dominant top-level categories;
- CLI and desktop versions or timing controls actually observed;
- confirmed facts, likely correlations, and unverified hypotheses separately;
- exact cleanup candidates and the evidence still required before each mutation; and
- that no state was changed, unless separately approved cleanup was completed and verified.

# Codex Home Cleanup Playbook

Read this file only after the user asks for cleanup, not for a read-only audit.

## Evidence boundary

Current official documentation confirms that Codex uses `$CODEX_HOME/sessions` and `$CODEX_HOME/archived_sessions`, that desktop and CLI builds can differ, and that frequent scheduled tasks can create many worktrees. It does not establish that every SQLite file is disposable, that a particular database will be rebuilt safely, or that antivirus exclusion is recommended.

Codex issue reports also document cases where a subagent rollout has reached `task_complete` or has no live handle while the desktop still displays it as `Active / Working` because a stored spawn edge remains open. Treat the live registry and terminal rollout event as execution evidence; do not infer that a stale badge is consuming a worker.

Refresh these sources before acting:

- [Codex troubleshooting](https://learn.chatgpt.com/docs/reference/troubleshooting)
- [Codex Git worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees)
- [Codex config basics](https://learn.chatgpt.com/docs/config-file/config-basic)
- [Completed subagent remains Active / Working on Windows](https://github.com/openai/codex/issues/38364)
- [Terminal rollout with an open spawn edge](https://github.com/openai/codex/issues/35209)
- [Stale multi-agent watched status](https://github.com/openai/codex/issues/37916)

Treat community cleanup reports as hypotheses until the target installation supplies matching evidence.

## Mutation preconditions

Before any move, deletion, worktree removal, uninstall, process stop, or security exclusion:

1. Record the resolved absolute `CODEX_HOME` and exact target.
2. Verify that the target stays inside the intended state directory or exact Git worktree.
3. Finish or pause active tasks and close all clients that may write the state.
4. Decide whether the item is a cache, log, transcript, credential store, project checkout, or unknown state.
5. Choose a rollback path. Prefer app-supported archive, backup, or quarantine before deletion.
6. Obtain explicit approval for the exact action and target.

## Multiple installations or processes

- Record client names, versions, executable paths, and observed `CODEX_HOME` values without exposing credentials.
- Distinguish an installed old build from a concurrently running writer.
- If the user chooses to remove an obsolete client, preserve its unique configuration and confirm the retained client starts and reads the intended state first.
- Do not assume reinstalling clears shared state; measure the state directory independently.

## Worktrees

Use Git-native inspection from the owning repository:

```text
git worktree list --porcelain
git -C <exact-worktree-path> status --short --branch --untracked-files=all
git -C <exact-worktree-path> status --short --ignored
git worktree prune --dry-run
```

For every removal candidate, check:

- whether its branch or detached commit contains unmerged work;
- tracked modifications and staged changes;
- untracked files;
- ignored files such as `.env`, local credentials, generated data, or downloaded assets; and
- whether an active or pinned Codex task still owns it.

Only after exact approval, use the owning repository's normal `git worktree remove` flow on that one path. Do not use force to bypass unresolved changes. Run `git worktree prune --dry-run` again before any prune, then verify the repository and retained worktrees.

## Databases, logs, sessions, and caches

- Identify the creating process and current purpose before classifying a file.
- Never print database contents, transcript names, tokens, or session identifiers into a shared report.
- For undocumented databases, prefer a closed-client backup or quarantine experiment: move one approved file to a recoverable location, start the retained client, verify startup and important history, then decide whether the backup can be removed later.
- Treat transcripts and archived sessions as user data. Use the app's archive controls or an approved export/backup path when available.
- Remove only a cache or log whose regeneration and loss impact have been established for the current version.

## Stale subagent or task status

- Compare the live agent registry, the rollout's last meaningful terminal event, and the stored UI relation read-only. A stale `open` relation alone does not prove that a worker is alive.
- Use supported task archive or close controls first, then refresh or restart the desktop client. Archiving is preferable because it is visible and reversible.
- Do not edit spawn-edge rows or other Codex SQLite state while the app is running. A direct database rewrite is unsupported cleanup and can race with the owning process.
- If the supported archive succeeds but the Subagents panel still says `Working`, report it as a UI/state-reconciliation defect rather than repeatedly interrupting a nonexistent worker.

## Antivirus exclusions

An exclusion reduces scanning cost and security coverage. Consider it only when high file count is confirmed, security-tool activity correlates with the slowdown, ordinary cleanup is insufficient, and the user accepts the tradeoff. Scope it to the smallest exact state or cache directory; never exclude the whole user profile, workspace root, or drive. Record how to remove the exclusion and verify the app before and after.

## Verification

After each approved mutation:

1. Re-run the metadata audit.
2. Start only the retained client and measure the same control and desktop path.
3. Verify required chats, configuration, Skills, plugins, and project state.
4. Check Git worktree and repository status when a worktree changed.
5. Stop if the expected signal does not improve; do not continue deleting unrelated state.

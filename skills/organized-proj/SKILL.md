---
name: organized-proj
description: Reconcile a project's affected documentation after a development stage, correct stale or duplicated guidance, and preserve useful results and lessons. Use when the user asks for organizedProj, project-doc cleanup, or a documentation close-out. A generic request to organize files, summarize a chat, or finish a small code edit is not enough to trigger this workflow.
---

# organizedProj

Make the project easy to resume: a reader should find the current task, understand relevant design, and see what was actually verified without reconstructing a conversation.

## Establish the scope

1. Identify the owning workspace, requested stage, and whether the request is review-only or authorizes edits. Inspect applicable instructions and the current branch/diff; protect unrelated work.
2. Start from the affected code, user-facing behavior, and existing document entry points. Read the relevant plan, design, worklog, and usage guidance—not every document or every project mentioned in chat.
3. Reuse existing equivalent paths. Do not install a new documentation layout, edit global instructions/memories, or deploy this Skill as a side effect of a project close-out.

For unclear document placement or conflicting records, read [the editing guide](references/editing-guide.md). It explains how to keep one maintained source for each fact.

## Reconcile only what changed

- Verify claims against the relevant code, configuration, tests, artifacts, or actual interface. Distinguish completed, verified, and still unverified work; a chat claim alone is not proof of an implementation result.
- Update the existing authoritative passage instead of appending a competing correction. Link to it from other entry points; do not copy implementation details into `AGENTS.md` as a second record.
- In a selected three-directory workflow, `active/` holds the current spec/plan, `design/` the stable algorithm/interface/architecture, and `worklog/` a completed stage's results and lessons. Update a category only when its content materially changes. A small edit may need only one existing paragraph—or no documentation change.
- Check affected user-facing instructions as part of the feature: relevant `--help`, setup instructions, examples, UI text, or tool descriptions. Do not rewrite the rest of a README for one changed option.
- Keep useful explanations of constraints and design choices. Remove debate transcripts, abandoned options, and commentary about features that were never required from current guidance. Preserve dated historical records rather than rewriting history to match today's design.
- Capture a reusable lesson as: what happened, supporting evidence, when the lesson applies, and what to do next time. Put ongoing design consequences in design documentation; keep incident-specific evidence in the worklog. Do not turn one mistake into a global ban.
- Use the project's worklog template when a substantial stage deserves a record. Retain supported dates, results, evidence, remaining work, and the next action; do not invent a date or generate a command transcript.

## Leave a clean, restartable workspace

- Close a completed plan according to the existing project convention. If moving or deleting a pre-existing file is not authorized, mark its state and propose the exact move instead of doing it silently. Do not create an extra handoff or archive hierarchy just for this Skill.
- Remove only task-created scratch that is within the cleanup authorization and whose useful content is already retained. Preserve existing documents, ignored data, experiments, and checkpoints unless separately authorized.
- Keep private sessions, credentials, host inventories, and local configuration out of public documents. Project-generated docs stay in the owning workspace, not an agent's state directory.
- Local documentation is sufficient to finish. Cloud archiving, publishing, Git operations, remote edits, and global Skill deployment require matching authorization; they are not implied by document cleanup.

## Verify and finish

Review the focused diff, changed links, and affected examples. Run the relevant documented command or interface check when practical and safe; state any missing evidence. Do not rerun unrelated suites or demand a new test count for prose changes.

Report the changed documents, the useful lesson retained, and anything still unverified or requiring a decision. A review-only request ends with findings and concrete proposed edits, not filesystem changes. Stop once this scope is reconciled.

## Maintaining this Skill

Run `python -B skills/organized-proj/scripts/check.py --skip-global` from the source repository. The check validates packaging and links, not whether an agent followed the workflow. Use [behavioral scenarios](tests/scenarios.md) to evaluate trigger accuracy and editing judgment in isolated fixtures before claiming behavioral validation. Source edits and installation are separate operations.

---
name: organized-proj
description: Reconcile project records after a meaningful stage or an explicit request for organizedProj, documentation cleanup, or a handoff. Keep current state, evidence, and the next action in existing records. Small edits and status recaps alone do not trigger document changes or fresh acceptance runs.
---

# organizedProj

Leave one maintained entry from which work can resume, with links to supporting detail. Reuse the project's documentation.

## Establish the scope

1. Identify the current goal, owning workspace, and requested result. Review-only requests produce findings; small edits with no durable result need no record. Preserve unrelated work.
2. Start at the existing current plan or progress entry and follow only relevant links. Reuse stage evidence tied to the affected version and environment; inspect changes or unresolved claims, not the entire project or conversation history.
3. Reuse existing paths. If no record exists and continuity needs one, create one project-local note. This Skill does not install a directory layout, edit global instructions, or deploy itself.

For unclear placement, stale records, or handoff needs, read [the editing guide](references/editing-guide.md).

## Reconcile only what changed

- Update the authoritative passage; link to details instead of copying them into another report or `AGENTS.md`. Touch only records whose content changed.
- Keep the current entry sufficient to continue: goal, relevant state and decisions, evidence locations, unfinished work, and the next action. Include the active worktree or runtime entry when needed to avoid resuming in the wrong place.
- Distinguish implementation, validation, deployment, and user acceptance wherever their states differ. Cover every agreed target; a local fix or documentation update does not prove delivery elsewhere. An assistant's claim alone is not implementation evidence.
- Update superseded current guidance in place. Preserve dated historical results with their applicable version or conditions; add a supersession link where readers could mistake them for current instructions. Age alone does not make a record obsolete.
- Keep README content focused on purpose, capabilities, first use, and material limitations. Update affected help and examples; put diagnostics and stage history in their existing records.
- Retain useful design reasons; remove abandoned debate and repeated qualifications from current guidance. Record reusable lessons with their evidence and scope in the owning project, without turning an isolated error into a global rule.
- Use an existing worklog only when there is new durable history to preserve. Record supported dates and outcomes, not command transcripts or a second copy of the current plan.

## Leave a clean, restartable workspace

- Close the plan using the project's convention. The maintained entry serves ordinary handoff; create a separate handoff only when requested or required by the destination, linking to maintained facts rather than duplicating them. Moves and deletions need matching authorization.
- Remove only task-created scratch that is within the cleanup authorization and whose useful content is already retained. Preserve existing documents, ignored data, experiments, and checkpoints unless separately authorized.
- Keep private sessions, credentials, host inventories, and local configuration out of public documents. Project-generated docs stay in the owning workspace, not an agent's state directory.
- Local documentation is sufficient to finish. Cloud archiving, publishing, Git operations, remote edits, and global Skill deployment require matching authorization; they are not implied by document cleanup.

## Verify and finish

Review the changed passages and links. Reuse applicable acceptance evidence; rerun a command only for a changed behavior or example, a concrete evidence gap that matters to this task, or an explicit request. A recap or handoff is not a new acceptance cycle. State missing evidence instead of expanding documentation cleanup into implementation work.

Report the maintained entry, relevant result, and any remaining decision or evidence gap. Stop when this scope is reconciled.

## Maintaining this Skill

Run `python -B skills/organized-proj/scripts/check.py` from source; add `--check-global` after authorized installation. The check validates packaging and links. Use [behavioral scenarios](tests/scenarios.md) when evaluating trigger accuracy and editing judgment.

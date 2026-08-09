# Workspace Continuous Documentation Rule Reference

English | [中文](workspace-continuous-documentation.zh-CN.md)

This guide explains all six rules in the [project AGENTS snippet](../templates/workspace/AGENTS.docs-workflow.md) and why every field exists in the [project-state template](../templates/workspace/project-state.md). IDs `D1` through `D6` follow the AGENTS snippet's bullet order exactly.

## Core Concepts

### Canonical Source

A canonical source is the accepted current version of one kind of information. Interface design may be canonical in `docs/architecture.md`, while resumable current state may be canonical in `docs/project-state.md`. One source prevents conflicting `final`, `v2`, and handoff copies; other documents link to it instead of duplicating it.

### Living Project-State

A living project-state is an in-place updated restart entry point. It stores only the current goal, verified state, next safe action, and open risks, not full history. Completed material is archived and removed from living state so the file stays short and current.

### Durable Knowledge

Durable knowledge remains valuable after the session: architecture decisions, failure boundaries, compatibility contracts, reliable verification methods, and user-corrected rules. Command transcripts, temporary logs, and obsolete intermediate guesses usually are not durable knowledge.

### Verified State

Verified state is the most recent project condition confirmed by code, tests, builds, the real interface, hardware, or other direct evidence. It records the method and date so a future session does not treat an old conclusion as current fact.

### Next Safe Action

The next safe action is a concrete next step that is safe under current evidence and risk boundaries, including its precondition and post-action verification. It lets the next agent continue without rediscovery or blind replay of a dangerous command.

### Worklog, Changelog, and Handoff

- A worklog records completed objectives, decisions, results, and problems for human review.
- A changelog records version- or user-facing changes.
- A handoff is a temporary transfer to a named consumer, not a permanent knowledge base.

Durable handoff content moves into project-state, architecture, decisions, or worklog, after which the task-created temporary file is closed.

## AGENTS Rules: D1-D6

| ID | Meaning | Development impact |
| --- | --- | --- |
| D1 | Read project-state and its routed architecture, decision, verification, and worklog docs before non-trivial work. | Work continues from established facts, reducing rediscovery, conflicting implementations, and forgotten failures; small tasks do not load every document. |
| D2 | Project `AGENTS.md` stores stable rules and routing, not task status, command transcripts, or host state. | Instructions stay small and durable, and startup context avoids stale progress and machine noise. |
| D3 | Before meaningful phase completion or possible context loss, update durable decisions, verified state, acceptance evidence, next safe action, and risks. | Interruptions resume from trustworthy state; recording state transitions rather than every edit preserves agile speed. |
| D4 | Prefer one living project-state; temporary handoffs need a consumer and closure plan, then are merged and cleaned up. | Prevents handoff accumulation and conflicting state files without removing real transfer capability. |
| D5 | Reuse existing worklog, changelog, architecture records, and naming instead of creating a parallel system. | Lowers maintenance and information forks; templates adapt to the project rather than forcing the project to adapt. |
| D6 | Before finishing, verify references, reconcile task notes, preserve user docs, and leave the workspace clean. | Prevents dead links, scratch files, and orphaned artifacts without using cleanliness to delete unknown-value material. |

## Project-State Fields: S1-S7

| ID | Field | Concept and development impact |
| --- | --- | --- |
| S1 | `Last verified` | Records when direct evidence last confirmed state, not merely when the file was edited. Old dates trigger revalidation. |
| S2 | `Scope and Current Goal` | Defines scope, current objective, and real acceptance signal, preventing a local task from expanding into an unintended rewrite. |
| S3 | `Verified State` | Captures confirmed facts, working paths, relevant branch/version/environment, and method so resumption uses evidence rather than session memory. |
| S4 | `Decisions` | Preserves the decision, rationale, rejected alternatives, and compatibility boundary, reducing repeated debate and accidental architectural reversal. |
| S5 | `Next Safe Action` | States the next step, precondition, and verification so handoff advances directly without replaying side-effecting operations blindly. |
| S6 | `Open Risks and Unknowns` | Makes assumptions, impact, and resolution path explicit instead of hiding uncertainty under “done.” |
| S7 | `Durable History` | Links existing worklogs, changelogs, or decisions and moves completed detail out of living state, keeping the restart entry concise. |

## Effect on Development Pace

Continuous documentation is not a report after every save. Useful triggers are an architecture or compatibility decision, changed real acceptance result, important failure boundary, meaningful phase completion, or approaching context compaction or transfer. A low-risk small edit only needs assurance that existing docs did not become false.

It deploys independently from host-global AGENTS. When paired, global rules govern general behavior and workspace rules provide project knowledge. Essential project rules stay in the repository because collaborators cannot be assumed to share one global file.

See [Host-Global AGENTS Rule Reference](global-agents.md) for the host-side rules.

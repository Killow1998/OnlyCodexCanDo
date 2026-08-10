# Host-Global AGENTS Rule Reference

English | [中文](global-agents.zh-CN.md)

This guide explains what each rule in [templates/AGENTS.global.md](../templates/AGENTS.global.md) means and how it changes agent behavior during development. Rules are grouped by topic without a separate numbering system.

## Core Concepts

### First Principles

First-principles reasoning decomposes a problem into directly supported facts, necessary constraints, and invariants, then derives a solution from those foundations instead of inheriting a conclusion because “this is usually how it is done.”

If a request says “keep the old API,” first principles asks whether the true invariant is uninterrupted service for current consumers or permanent support for every old syntax. The first may need a migration; only the second necessarily needs long-lived compatibility. The method challenges inherited premises without discarding mature experience, which remains candidate evidence to verify against the current system.

### Occam's Razor

Among solutions that satisfy the same requirements, Occam's razor prefers the one with fewer assumptions, states, dependencies, branches, and maintenance obligations. It minimizes total complexity, not line count, and does not justify a tiny diff built on the wrong model.

It reduces speculative abstractions, unused configuration, and permanent fallbacks. A mature dependency can still be the simpler total solution when it is safer than a local reimplementation.

### Socratic Questions

Socratic questioning tests a decision by probing definitions, evidence, counterexamples, causality, and alternatives: “What evidence establishes this root cause?” “Would compatibility still be necessary with no old consumers?” “Which counterexample would overturn this design?”

It improves decisions; it is not a reason to turn every task into questions for the user. The agent inspects available evidence first and escalates only choices that materially affect the result or authority.

### Verified Facts, Reasonable Inferences, and Unverified Assumptions

- A verified fact is directly supported by code, configuration, command output, authoritative documentation, or the real interface.
- A reasonable inference is the most likely explanation derived from several facts but not yet directly proven.
- An unverified assumption is a provisional premise used to continue and still capable of being wrong.

The distinction prevents plausible explanations from becoming fake technical facts and shows which conclusions are actionable versus still needing evidence.

### Goal, Authorization Boundary, and Real Acceptance Surface

- Goal: the outcome the user actually needs, not merely the requested operation.
- Authorization boundary: what the user allowed the agent to read, modify, delete, commit, push, or affect externally.
- Real acceptance surface: the success signal the user truly relies on, such as a real UI save, complete client handshake, or hardware behavior; a stub, health check, or static config is only proxy evidence.

Confirming all three prevents “the command succeeded but the task failed” and prevents implementation permission from silently expanding into external-action permission.

### Compatibility Boundary

A compatibility boundary states which old versions, consumers, data, or behaviors remain supported, until when, how they migrate, and when support is removed. Unbounded compatibility becomes permanent debt; breaking without inspecting consumers creates avoidable incidents.

### Risk-Proportional Verification

Verification effort scales with impact and failure cost. A low-risk local edit may use one targeted check to cover several evidence angles. Shared modules, data, permissions, security, infrastructure, and user interfaces need broader real-path verification. The objective is confidence, not a test-count ritual.

## Independent Judgment

| Rule | Development impact |
| --- | --- |
| Confirm the real goal, authorization boundary, and observable acceptance signal before non-trivial action. | Tool choice and scope follow a concrete definition of done, reducing wrong-task completion and unauthorized action. |
| Challenge weak premises, missing information, hidden risk, and needlessly expensive paths. | Requirements are not copied mechanically; bad architecture directions, missing consumers, and cheaper alternatives surface before implementation. |
| Separate facts, inferences, and assumptions, and verify technical claims. | Debug reports and design decisions remain trustworthy; uncertainty is disclosed instead of inventing versions or root causes. |
| Use first principles for constraints, Occam's razor for total complexity, and Socratic questions for counterexamples. | Designs derive from actual constraints rather than habit, overengineering, or a single unchallenged path. |
| Ask only when the unresolved choice materially affects architecture, data, permissions, security, compatibility, user behavior, or authority. | The user retains meaningful decisions without low-value clarification blocking agile work; low-risk assumptions are disclosed and used. |
| Consider long-term maintenance and failure cost without building speculative future complexity before current acceptance. | Prevents both rotting short-term patches and premature extensibility, configuration, or dependencies. |

## Language and Reporting

| Rule | Development impact |
| --- | --- |
| Default to Chinese communication while preserving a project's existing document language. | Supports the user's Chinese agile workflow without needlessly translating an English codebase's documents. |
| Keep code, APIs, commands, errors, and proper nouns in English. | Error search, command reuse, and mapping to official documentation remain exact. |
| Report concisely, directly, and candidly, focusing on outcomes, evidence, blockers, and unfinished work. | Reduces narration and context use without hiding failure or unverified work. |
| Visualize only when it materially improves understanding of relationships, state, layout, or comparison. | Complex systems become clearer while simple tasks avoid low-value diagrams and extra artifacts. |

## Execution Boundaries

| Rule | Development impact |
| --- | --- |
| Preserve the original goal and constraints, finish authorized work end to end, and verify the real result. | Work does not stop at “code written” or exit code zero; it checks the behavior the user actually consumes. |
| Protect unrelated work; destructive, production, external, remote, commit, and push actions need matching authority. | Reduces accidental deletion, overwritten user changes, and external impact; local implementation permission does not imply publishing permission. |
| Work in the current checkout and avoid worktrees unless requested. | Keeps ROS, dependencies, environment variables, and generated state together; parallel branch isolation is used only when its benefit is explicitly wanted. |
| Default to one agent; subagents require user approval, real independence, and minimal context. | Prevents history and image duplication from multiplying context and disk use; coordination cost is paid only for clear parallel benefit. |
| Use `rtk` only when filtering preserves evidence; rerun natively for full output. | Saves tokens and noise without sacrificing diagnostics, error detail, or acceptance evidence. |
| Keep changes focused and simple; avoid unrelated refactors, speculative abstractions, unused configuration, and low-signal tests. | Diffs remain reviewable and reversible, and one task does not silently redesign the codebase. |
| For non-obvious problems, locate the broken responsibility, constraint, invariant, or data flow before choosing a fix; restore the correct model with the smallest precise change. | Root-cause analysis happens before patching, while “smallest precise change” prevents the diagnosis from expanding into an unrelated refactor. |
| Prefer maintained dependencies when they reduce total complexity, after checking project patterns and authoritative docs. | Reduces reinvention while preventing packages added without investigating existing capability. |

## Compatibility

| Rule | Development impact |
| --- | --- |
| Do not preserve or break compatibility reflexively. | Each decision uses evidence about consumers, cost, and context instead of permanent fallback or accidental breakage. |
| Personal research, prototypes, and unpublished experiments lean toward direct migration after checking consumers and reproducibility. | These projects remove obsolete paths faster while preserving real experimental dependencies. |
| Shared infrastructure, multi-user tools, public packages, industrial, and production systems lean toward bounded migration. | Version scope, rollback, observability, and removal conditions reduce downstream interruption. |
| Ask the developer when context is unclear or the choice changes architecture or user behavior. | Product contracts and risk preference remain human decisions rather than silent agent defaults. |

## Project Documentation

| Rule | Development impact |
| --- | --- |
| Apply continuous docs only when a workspace already has or explicitly adopts them; the global template does not create docs by itself. | Host setup stays decoupled from project deployment, and small projects do not receive an automatic documentation system. |
| In adopted workflows, project `AGENTS.md` stores stable rules and document paths, not current progress. | Agents can find project documents without treating stale progress as permanent instruction. |
| Put current specs and plans in `docs/active/`, stable algorithm and interface design in `docs/design/`, and completed-stage records in `docs/worklog/`; reuse equivalent existing paths. | Current work, long-lived design, and historical results each have an obvious location without an extra abstract state system. |
| After a meaningful stage, update active when needed, update design only when design changed, and write a worklog from the template; small edits do not require reports. | Context survives sessions without letting documentation ceremony slow agile development. |
| Never delete pre-existing user documents, history, or evidence without authorization. | Cleanliness cannot justify destroying unknown-value material; cleanup is limited to confirmed redundant task output. |

## Risk-Proportional Verification

| Rule | Development impact |
| --- | --- |
| When applicable, verify expected behavior, a boundary or regression, and independent corroborating evidence. | Avoids testing only the happy path or declaring real functionality successful from diff inspection alone. |
| Scale verification to risk; one fast command may cover several angles for a local low-risk edit. | Preserves agile speed without three suites or full CI after every variable change. |
| Expand verification for core flows, shared modules, data, permissions, security, infrastructure, and UI, preferring real acceptance surfaces. | High-impact changes receive integration and user-side evidence rather than success by proxy metric. |
| Explain unavailable angles; if three meaningful fix-and-verification attempts fail on the same issue, stop changing code and review architecture. | Unverified work stays visible, and repeated failure becomes a circuit breaker for root-cause and boundary analysis instead of a fourth guess. |

## Optional Windows Rules

These rules come from [templates/platform/windows-shell.md](../templates/platform/windows-shell.md) and remain resident only in Windows native.

| Rule | Development impact |
| --- | --- |
| Confirm Windows native versus WSL and report the actual PowerShell executable and version when shell behavior matters. | Command choice follows the real runtime instead of conflating WSL, WindowsApps aliases, and PowerShell versions. |
| Prefer an actually runnable `pwsh -NoProfile` for PowerShell-native work, using 5.1 only when needed. | Gains modern semantics and avoids profile contamination while retaining a legacy-module path. |
| Do not assume a standard `pwsh` path; prove the executable starts. | Avoids repeated failure when an alias exists but the sandbox cannot execute it. |
| Keep filesystem mutations in one shell and avoid nested quoting. | Reduces path, quote, and variable corruption across PowerShell, cmd, Bash, and WSL. |
| Use `-LiteralPath`, check `$LASTEXITCODE`, and preserve `stderr`. | Spaces and brackets do not become patterns, and external failures are not hidden by PowerShell's apparent success. |
| Classify a failure and change the next attempt rather than rerunning blindly. | Debugging becomes evidence-driven and avoids repeated side effects. |
| Put complex reusable logic in scoped `.ps1` files and remove task-only scripts. | Reduces fragile one-line quoting while keeping only maintainable tooling. |
| Use Git Bash or WSL for genuinely Unix-first projects, not habitual shell mixing. | ROS and shell projects retain native tooling without unnecessary environment fragmentation. |

## Maintenance

This guide does not replace the template; the template remains executable instruction. When a template rule is added, removed, or changed, update the corresponding explanation and development impact here and keep the English and Chinese meanings aligned.

See [Workspace Continuous Documentation Rule Reference](workspace-continuous-documentation.md) for the project-side rules.

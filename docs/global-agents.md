# Host-Global AGENTS Core and Option Reference

English | [中文](global-agents.zh-CN.md)

This guide explains the development effect of the minimal core in [templates/AGENTS.global.md](../templates/AGENTS.global.md) and the choices under [templates/optional/](../templates/optional/) and [templates/platform/](../templates/platform/). The core is broadly applicable; every other module requires an explicit user choice after its behavior and tradeoff are explained.

The core opens with “I'm glad to work with you, explore, and create together.” It frames the rules as an improvable collaboration agreement, not a command to agree with the user or repeat a greeting every turn. Personal names remain an independent private option.

## Concepts behind the core

### First principles

First-principles reasoning decomposes a problem into directly supported facts, necessary constraints, and invariants, then derives a solution from those foundations instead of inheriting a conclusion because “this is usually how it is done.” Mature experience remains candidate evidence, not an unquestionable premise.

### Occam's razor

Among solutions that satisfy the same requirements, Occam's razor prefers fewer assumptions, states, dependencies, branches, and maintenance obligations. It minimizes total complexity, not line count, and does not justify a tiny diff built on the wrong model.

### Socratic questions

Socratic questioning probes definitions, evidence, counterexamples, causality, and alternatives. It improves decisions without turning every task into a questionnaire: the agent inspects available evidence first and asks only about choices that materially change the result or authority.

### Facts, inference, assumptions, and acceptance

- A verified fact is directly supported by code, configuration, command output, authoritative documentation, or the real interface.
- A reasonable inference is the most likely explanation derived from facts but not yet directly proven.
- An unverified assumption is a provisional premise that may still be wrong.
- The real acceptance surface is the success signal the user actually depends on, not a convenient health check or static proxy.

### Compatibility and verification boundaries

A compatibility boundary identifies which consumers, versions, data, or behaviors remain supported, how migration works, and when compatibility ends. Verification effort then scales with the impact and failure cost of the change. Neither permanent compatibility nor three full test suites is a universal default.

## Minimal core rules

| Core rule | Development impact |
| --- | --- |
| Identify the real goal, authorization boundary, and observable acceptance signal; challenge weak premises and separate verified facts, reasonable inferences, and assumptions. | Scope follows a concrete definition of done, while plausible explanations do not become invented technical facts. |
| Use first principles, Occam's razor, and Socratic counterexamples; consider maintenance and failure cost without speculative future complexity. | Designs follow necessary constraints and total complexity instead of habit, line count, or premature extensibility. |
| Ask only about unresolved material decisions; do not ask again for an unchanged decision already authorized. | Users retain meaningful decisions without repeated approvals blocking agile work. |
| Apply relevant Skills within the task; explicit user instructions take precedence over Skill guidelines, subject to higher-priority instructions and permissions. Identify rules that block progress or change scope. | An imported workflow cannot silently add interviews, delegation, external writes, or approval rituals to the task. |
| Preserve the goal, finish authorized work, then compare every requested target with the actual change, evidence, and unfinished work without expanding scope merely because budget remains. | The agent does not stop at “code written,” overlook another host or output, quietly add adjacent work, or confuse capacity with authorization. |
| Protect unrelated work and require matching authority for destructive, production, external, remote, commit, or push actions; keep secrets and private runtime data out of shared output. | Local implementation permission does not silently expand into data loss, publication, or credential exposure. |
| Make the simplest focused change that fully meets the requirement. | Diffs remain reviewable and avoid unrelated refactors, speculative abstractions, unused configuration, and low-signal tests. |
| Implement the requested behavior without adjacent features or narrative residue about unrelated omissions. | UI, help, docs, code, tests, and publication summaries describe the product and delivered change—not the prompt, internal constraints, or a history of unnecessary work. |
| Do not add defensive machinery, fallback paths, or bespoke validation without a concrete failure boundary and evidence that ordinary mechanisms are insufficient; preserve existing and high-risk safeguards. | Defensive preparation cannot become an unbounded substitute for the requested work, while real high-risk boundaries retain appropriate protection. |
| For a non-obvious problem, locate the broken responsibility, constraint, invariant, or data flow before fixing it. | Root-cause analysis happens before patch stacking, while the fix remains bounded to the correct model. |
| Classify a failure and change the next attempt; after three meaningful unresolved attempts, review architecture, data flow, dependencies, and the failure boundary. | Debugging gains new evidence, avoids repeated side effects, and switches from guessing to model review when necessary. |
| Decide compatibility from consumers, reproducibility, failure cost, and migration evidence; ask when the choice is material. | Prevents both permanent fallback debt and accidental breakage. |
| Check project patterns and authoritative documentation before major architecture, dependency, permission, security, or user-visible changes. | Reduces reinvention and decisions based on stale or imagined framework behavior. |
| Remove task-created debug and temporary artifacts unless they become maintained assets. | The workspace remains clean without deleting pre-existing user material. |
| Seek expected behavior, a relevant boundary or regression, and independent corroboration when applicable. | Verification covers more than the happy path or the diff itself. |
| Scale verification to risk; after relevant checks pass, repeat or expand only for new changes, failures, or unresolved concerns. | Low-risk edits stay fast, high-impact changes get appropriate evidence, and verification has a stopping condition. |
| Prefer the real acceptance surface and explain unavailable or inapplicable evidence. | Proxy success does not replace user-consumed behavior, and remaining uncertainty stays visible. |
| Report outcomes, evidence, blockers, uncertainty, and unfinished work concisely and candidly. | Users receive decision-relevant information without noisy narration or hidden failure. |
| Visualize only when it materially improves understanding. | Complex relationships gain clarity while simple tasks avoid low-value diagrams and artifacts. |

## Optional host modules

Optional does not mean low value. It means that the rule expresses a user preference, assumes a tool or runtime, or carries a cost that is not universal.

| Module | What it adds | Selection question and tradeoff |
| --- | --- | --- |
| [Chinese-first communication](../templates/optional/chinese-first.md) | Chinese conversation and prose while technical identifiers remain English. | Does the user want Chinese as the normal working language? It improves fluency for Chinese users but is wrong as a public universal default. |
| [Collaboration names](../templates/optional/collaboration-names.md) | Natural use of a chosen user name and agent nickname. | Would the user like personal forms of address? Ask for both names and replace the placeholders; keep the values private and out of authorship or account identities. |
| [Session titles](../templates/optional/session-titles.md) | One-time naming of the current task after its topic is clear, using its creation date and a selected time zone. | Does the user want Chinese sidebar labels, and can this host read task metadata and safely rename it? Choose the time zone independently of conversation language; see the capability limits below. |
| [Focused delegation](../templates/optional/subagent-context.md) | Independent subtasks with fresh, minimal context; scoped ownership and result collection. | Is useful parallel work available and allowed, and can this client start without inherited history? The main agent must still integrate and stop obsolete work. |
| [Current-checkout workflow](../templates/optional/no-worktrees.md) | Avoids Git worktrees unless requested. | Does environment cohesion matter more than branch isolation? This is often relevant to ROS, hardware, generated state, or manually sourced environments. |
| [RTK](../templates/optional/rtk.md) | Selective output filtering with native reruns when full evidence is needed. | Is RTK installed, and does the user accept that filtering can hide detail? Token savings must not reduce diagnostic ability. |
| [Recorded time zone](../templates/optional/timezone.md) | Uses a chosen IANA time zone for agent-created worklogs and experiment records while preserving source timestamps. | Which time zone should records use? The placeholder must be replaced before installation. |
| [Repository safety](../templates/optional/repository-safety.md) | Pre-write branch/status inspection, strict protection of unrelated changes, repository-boundary preservation, and explicit Git publication authority. | Does this host routinely modify Git repositories and benefit from stronger operational ceremony? |
| [Data migration safety](../templates/optional/data-migration-safety.md) | Requires target, risk, rollback, and consumer verification for schema or persistent-data changes. | Can this agent touch durable data? The added preflight is valuable when data loss or recovery cost is real, but unnecessary on hosts that never do so. |
| [systemd resource limits](../templates/optional/systemd-resource-limits.md) | Uses user-level systemd scopes or services with selected memory and swap limits for heavy workloads. | Is Linux `systemd --user` available, does the host run memory-intensive jobs, and what headroom must remain? Never invent fixed limits. |
| [Windows shell](../templates/platform/windows-shell.md) | PowerShell/runtime detection, literal paths, exit-code handling, single-shell mutations, and Unix-first fallback guidance. | Is the agent actually Windows native, and does the user want these shell constraints resident globally? Runtime detection makes it relevant, not automatically approved. |

When replacing the former single-agent option, remove its conflicting ban in the approved deployment diff rather than appending the new module alongside it. The change allows bounded delegation without a new user confirmation for every subtask where current higher-priority instructions permit it; it does not expand filesystem, remote, or publication authority.

### What the Windows option changes

| Rule | Development impact |
| --- | --- |
| Confirm Windows native versus WSL and report the actual PowerShell executable and version when shell behavior matters. | Command choice follows the real runtime instead of conflating WSL, aliases, and PowerShell versions. |
| Prefer an actually runnable `pwsh -NoProfile`, using Windows PowerShell 5.1 only when required. | Gains modern semantics without losing a legacy-module path. |
| Do not assume a standard `pwsh` path. | Avoids repeated failure when an alias exists but is not executable in the current environment. |
| Keep filesystem mutations in one shell. | Reduces quoting, path, and variable corruption across PowerShell, cmd, Bash, and WSL. |
| Use `-LiteralPath`, inspect `$LASTEXITCODE`, and preserve `stderr`. | Special paths and external failures remain observable. |
| Put complex reusable logic in scoped `.ps1` files and remove task-only scripts. | Reusable logic becomes maintainable without leaving temporary tooling behind. |
| Use Git Bash or WSL for genuinely Unix-first work when it reduces translation risk. | Unix-first projects keep their natural toolchain without habitual shell mixing. |

## How deployment should select modules

1. Read the minimal core, inspect the actual host and existing global `AGENTS.md`, and identify conflicts without writing. Classify existing rules as keep, rehome behind progressive disclosure, or propose for removal; non-conflicting does not automatically mean worth loading on every task.
2. Eliminate clearly irrelevant modules and rules that merely restate discoverable or drift-prone implementation details. Do not present a generic checklist merely because files exist.
3. For each remaining candidate, explain the behavior, benefit, cost, prerequisites, and recommendation in plain language.
4. Reuse choices the user has already made. Batch remaining preferences into a small set of questions through an available interactive choice tool, with concise explanations, recommended options, and free-text alternatives. Do not ask one question per file or silently accept preselected options. If the UI is unavailable, use one compact plain-language question.
5. Show the exact merged diff, module list, resolved parameters, and every proposed rule removal or rehome. Obtain authorization through the supported approval mechanism, then make a recoverable backup and apply it. Preference answers are not filesystem permission escalation; do not repeatedly request unchanged decisions or promise that every client can finish deployment in one interaction.
6. Verify that the core and selected modules appear exactly once, unselected modules are absent, parameter placeholders are resolved, and preserved local rules remain.

## Workspace modules remain separate

Host-global selection must not install project workflows. Continuous documentation, experiment records, and robotics validation are independent choices under [templates/workspace/](../templates/workspace/) and are deployed from inside a target repository. See [Workspace Continuous Documentation Workflow](workspace-continuous-documentation.md).

## What automatic session naming can actually do

The [session-title module](../templates/optional/session-titles.md) is an optional instruction, not an installed hook or background service. It uses `MMDD｜类型｜主题`, where the date comes from `createdAt` in the selected IANA time zone. It never substitutes `updatedAt` or today's date, guesses an unknown topic, or renames a project. Manual titles remain untouched.

Codex's [app-server API](https://learn.chatgpt.com/docs/app-server) exposes `thread/name/set`, but a particular agent session must also have an authorized, supported way to call it and read the necessary metadata. If title origin or metadata is unknown, leave the title unchanged. Configuring this module does not establish that the capability works on a given host.

A [SessionStart hook](https://learn.chatgpt.com/docs/hooks) can also fire on resume or compaction, before a new task's topic is clear. Hook configuration alone therefore does not provide reliable one-time semantic naming. A future integration must validate creation time, title ownership, repeated-event handling, and protection of manual edits. Do not edit internal databases or build a timer that repeatedly scans all histories as a shortcut.

The host acceptance check is a new task with a clear topic and a known creation timestamp: verify its displayed date/type/topic, then resume it and confirm its title does not churn. Verify a manually renamed task stays unchanged. Until these checks pass, report naming as configured or unavailable, not operational.

## Maintenance

The template and module files contain executable runtime instructions; this guide owns selection criteria, prerequisites, tradeoffs, and their effects. When a core or module rule changes, update this reference and its Chinese counterpart in the same change. Do not promote a personal preference into the core merely because one user selects it on every host.

# Host-Global AGENTS Core and Option Reference

English | [中文](global-agents.zh-CN.md)

This guide explains the development effect of the minimal core in [templates/AGENTS.global.md](../templates/AGENTS.global.md) and the choices under [templates/optional/](../templates/optional/) and [templates/platform/](../templates/platform/). The core is broadly applicable; every other module requires an explicit user choice after its behavior and tradeoff are explained.

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
| Identify the real goal, authorization boundary, and observable acceptance signal before non-trivial action. | Tool choice and scope follow a concrete definition of done, reducing wrong-task completion and unauthorized action. |
| Challenge weak premises and separate verified facts, reasonable inferences, and assumptions. | Plausible explanations do not become invented technical facts; cheaper or safer alternatives surface before implementation. |
| Use first principles, Occam's razor, and Socratic counterexamples. | Designs follow necessary constraints and total complexity instead of habit, line count, or a single unchallenged path. |
| Ask only when an unresolved decision materially changes architecture, data, permissions, security, compatibility, visible behavior, or authorization. | Users retain meaningful decisions without low-value clarification blocking agile work. |
| Consider maintenance and failure cost without building speculative future complexity. | Avoids both rotting stopgaps and premature extensibility. |
| Preserve the goal and finish authorized work through real-result verification. | The agent does not stop at “code written” or exit code zero when the user consumes another behavior. |
| Protect unrelated work and require matching authority for destructive, production, external, remote, commit, or push actions; keep secrets and private runtime data out of shared output. | Local implementation permission does not silently expand into data loss, publication, or credential exposure. |
| Make the simplest focused change that fully meets the requirement. | Diffs remain reviewable and avoid unrelated refactors, speculative abstractions, unused configuration, and low-signal tests. |
| For a non-obvious problem, locate the broken responsibility, constraint, invariant, or data flow before fixing it. | Root-cause analysis happens before patch stacking, while the fix remains bounded to the correct model. |
| Classify a failure and change the next attempt instead of blindly repeating it. | Debugging gains new evidence and avoids repeated side effects. |
| Decide compatibility from consumers, reproducibility, failure cost, and migration evidence; ask when the choice is material. | Prevents both permanent fallback debt and accidental breakage. |
| Check project patterns and authoritative documentation before major architecture, dependency, permission, security, or user-visible changes. | Reduces reinvention and decisions based on stale or imagined framework behavior. |
| Remove task-created debug and temporary artifacts unless they become maintained assets. | The workspace remains clean without deleting pre-existing user material. |
| Seek expected behavior, a relevant boundary or regression, and independent corroboration when applicable. | Verification covers more than the happy path or the diff itself. |
| Scale verification to risk. | Low-risk edits stay fast; high-impact changes receive integration, user-interface, data, or infrastructure evidence. |
| Prefer the real acceptance surface and explain unavailable or inapplicable evidence. | Proxy success does not replace user-consumed behavior, and remaining uncertainty stays visible. |
| After three meaningful failed fix-and-verification attempts, review architecture and failure boundaries. | Repeated failure triggers model review instead of a fourth guess. |
| Report outcomes, evidence, blockers, uncertainty, and unfinished work concisely and candidly. | Users receive decision-relevant information without noisy narration or hidden failure. |
| Visualize only when it materially improves understanding. | Complex relationships gain clarity while simple tasks avoid low-value diagrams and artifacts. |

## Optional host modules

Optional does not mean low value. It means that the rule expresses a user preference, assumes a tool or runtime, or carries a cost that is not universal.

| Module | What it adds | Selection question and tradeoff |
| --- | --- | --- |
| [Chinese-first communication](../templates/optional/chinese-first.md) | Chinese conversation and prose while technical identifiers remain English. | Does the user want Chinese as the normal working language? It improves fluency for Chinese users but is wrong as a public universal default. |
| [Single-agent default](../templates/optional/single-agent.md) | One agent by default; subagents require explicit authorization, independent work, and minimal context. | Does the user prefer lower context duplication and coordination cost over automatic parallelism? |
| [Current-checkout workflow](../templates/optional/no-worktrees.md) | Avoids Git worktrees unless requested. | Does environment cohesion matter more than branch isolation? This is often relevant to ROS, hardware, generated state, or manually sourced environments. |
| [RTK](../templates/optional/rtk.md) | Selective output filtering with native reruns when full evidence is needed. | Is RTK installed, and does the user accept that filtering can hide detail? Token savings must not reduce diagnostic ability. |
| [Recorded time zone](../templates/optional/timezone.md) | Uses a chosen IANA time zone for agent-created worklogs and experiment records while preserving source timestamps. | Which time zone should records use? The placeholder must be replaced before installation. |
| [Repository safety](../templates/optional/repository-safety.md) | Pre-write branch/status inspection, strict protection of unrelated changes, repository-boundary preservation, and explicit Git publication authority. | Does this host routinely modify Git repositories and benefit from stronger operational ceremony? |
| [Data migration safety](../templates/optional/data-migration-safety.md) | Requires target, risk, rollback, and consumer verification for schema or persistent-data changes. | Can this agent touch durable data? The added preflight is valuable when data loss or recovery cost is real, but unnecessary on hosts that never do so. |
| [systemd resource limits](../templates/optional/systemd-resource-limits.md) | Uses user-level systemd scopes or services with selected memory and swap limits for heavy workloads. | Is Linux `systemd --user` available, does the host run memory-intensive jobs, and what headroom must remain? Never invent fixed limits. |
| [Windows shell](../templates/platform/windows-shell.md) | PowerShell/runtime detection, literal paths, exit-code handling, single-shell mutations, and Unix-first fallback guidance. | Is the agent actually Windows native, and does the user want these shell constraints resident globally? Runtime detection makes it relevant, not automatically approved. |

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

1. Read the minimal core, inspect the actual host and existing global `AGENTS.md`, and identify conflicts without writing.
2. Eliminate clearly irrelevant modules. Do not present a generic checklist merely because files exist.
3. For each remaining candidate, explain the behavior, benefit, cost, prerequisites, and recommendation in plain language.
4. Ask the user to select modules. Detection and recommendation are not approval.
5. Show the exact merged diff and module list, then write only after confirmation and a recoverable backup.
6. Verify that the core and selected modules appear exactly once, unselected modules are absent, parameter placeholders are resolved, and preserved local rules remain.

## Workspace modules remain separate

Host-global selection must not install project workflows. Continuous documentation, experiment records, and robotics validation are independent choices under [templates/workspace/](../templates/workspace/) and are deployed from inside a target repository. See [Workspace Continuous Documentation Workflow](workspace-continuous-documentation.md).

## Maintenance

The template and module files remain executable instructions; this guide explains their effect. When a core or module rule changes, update this reference and its Chinese counterpart in the same change. Do not promote a personal preference into the core merely because one user selects it on every host.

# Host-Global AGENTS Guide

English | [中文](global-agents.zh-CN.md)

The [minimal core](../templates/AGENTS.global.md) is deliberately small. It keeps only rules that prevent scope drift, unauthorized loss, repeated errors, unsupported guesses, excessive verification, or missing stage records.

## Core behavior

- Judge by first principles, Occam's razor, and Socratic questioning.
- Change only the authorized scope and inspect the project before judging.
- Explain broad changes, learn from corrections, and require matching authority for external or hard-to-reverse actions.
- Test observable behavior and stop when evidence is sufficient.
- After a meaningful stage, commit only when authorized or preserve the result in existing project records.

The core does not prescribe a shell, operating system, directory layout, or fixed test ritual.

## Progressive project records

Stage records use [`organized-proj`](../skills/organized-proj/SKILL.md) as progressive disclosure. The global file contains only the trigger; the Skill contains the detailed close-out process and is read only after a meaningful stage. It reuses the project's existing documentation and skips small edits.

During global setup:

1. Check whether `organized-proj` is installed globally.
2. If absent, explain its behavior and ask once whether to install it from this repository.
3. If declined, omit the Skill reference and use a generic existing-record instruction.
4. Never ask again for each project or install a project documentation layout automatically.

See [Progressive Project Records](workspace-continuous-documentation.md).

## Optional host preferences

Add only preferences the user has actually selected:

| Module | Behavior |
| --- | --- |
| [Chinese-first](../templates/optional/chinese-first.md) | Uses Chinese prose while preserving technical identifiers. |
| [Collaboration names](../templates/optional/collaboration-names.md) | Uses private user and agent names. |
| [Subagents by explicit request](../templates/optional/subagent-context.md) | Prevents delegation until the user authorizes the current task or scope. |
| [No Git worktrees by default](../templates/optional/no-worktrees.md) | Keeps work in the current checkout unless requested otherwise. |
| [Recorded time zone](../templates/optional/timezone.md) | Applies a chosen IANA zone to agent-created records. |
| [Repository safety](../templates/optional/repository-safety.md) | Adds stricter Git and unrelated-work protections. |
| [UI verification](../templates/optional/ui-verification.md) | Avoids UI unit tests and gives visual acceptance to the user. |

Personal names and resolved host values stay out of the public template.

## Deployment

Inspect the existing global file, remove obsolete or repeated rules, and show the proposed result before writing. Ask only about unresolved choices. Back up the old file, apply the selected core and options once, and verify the read-back. Host-specific deployment does not authorize project edits, remote writes, commits, or publication.

For multiple hosts, compare the core and selected options separately. An unavailable host remains unverified; host inventories and private paths do not enter this repository.

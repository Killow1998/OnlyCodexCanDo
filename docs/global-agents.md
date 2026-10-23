# Host-Global AGENTS Guide

English | [中文](global-agents.zh-CN.md)

The [minimal core](../templates/AGENTS.global.md) keeps cross-task judgment, initiative, authorization boundaries, and stage records concise.

## Core behavior

- Judge by first principles, Occam's razor, and Socratic questioning.
- Search mature solutions during design and compare reuse with customization. Bring consequential architecture or lifecycle-cost choices to the user.
- Change only the authorized scope and inspect the project before judging.
- Explain broad changes, learn from corrections, and require matching authority for external or hard-to-reverse actions.
- Test observable behavior and stop when evidence is sufficient.
- After a meaningful stage, commit only when authorized or preserve the result in existing project records.
- At task completion, remove temporary artifacts and obsolete backups; ask the user first if unsure whether to keep them.

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
| [Collaboration names](../templates/optional/collaboration-names.md) | Sets private names and a collaborative opening that encourages independent judgment. |
| [Subagents by explicit request](../templates/optional/subagent-context.md) | Prevents delegation until the user authorizes the current task or scope. |
| [No Git worktrees by default](../templates/optional/no-worktrees.md) | Keeps work in the current checkout unless requested otherwise. |
| [Recorded time zone](../templates/optional/timezone.md) | Applies a chosen IANA zone to agent-created records. |
| [Repository safety](../templates/optional/repository-safety.md) | Adds stricter Git and unrelated-work protections. |
| [UI verification](../templates/optional/ui-verification.md) | Avoids UI unit tests and gives visual acceptance to the user. |

When selected, place the naming instruction first, followed by the collaborative opening, in the user's chosen language. Personal names and resolved host values stay out of the public template.

## On-demand development guides

These optional guides are ordinary Markdown files. Select the relevant guides once during global setup; no per-project installation or new Skill is needed.

| Guide | Read when | Focus |
| --- | --- | --- |
| [Backend](../templates/optional/guides/backend.md) | Backend or compiled algorithm work | Fast CMake/catkin/colcon iteration, bounded diagnostic logs, and independent interfaces. |
| [Frontend](../templates/optional/guides/frontend.md) | Designing or changing an interface | Information hierarchy, restrained presentation, interaction, and human visual acceptance. |
| [Review, commits, and pushes](../templates/optional/guides/git.md) | Review, commit, or push work | Requested simplification and review; ordinary Git operations do not trigger that pass. |

Copy only the selected language and guides to `guides/` beside the actual global `AGENTS.md`, using the canonical names `backend.md`, `frontend.md`, and `git.md`. Chinese sources use `.zh-CN.md` in this repository; rename them to the canonical names when installing. Preserve local edits during updates. Inspect existing project conventions when applying a guide.

If all three guides are selected, the global file needs one routing line:

```markdown
- Read the relevant guide beside this file: `guides/backend.md` for backend or algorithm work, `guides/frontend.md` for interfaces, and `guides/git.md` for code review, simplification, commits, or pushes.
```

Keep references only to installed guides. These are explicit instructions to read a file when needed; do not assume that an `@file.md` mention implements conditional loading. Keep the guide bodies out of the always-loaded core. Existing domain references under `templates/workspace/` remain optional; avoid installing overlapping UI instructions twice.

The guides set concrete outcomes: fast iteration, useful bounded logs, independent interfaces, and working user flows. Frontend sizes and timings are starting choices for rendered review. File length guides responsibility review rather than mandatory splitting. Reuse established checks and useful short scripts. A simplification request calls for active structural improvement; a review-only request produces findings. Ordinary commits and pushes do not trigger a separate simplification pass.

For an always-loaded coding preference, select this sentence:

> Follow the single-responsibility principle and use searchable names. Comments add only information that the code does not express.

## Concise, candid reporting

For this selected preference, replace the existing reporting line rather than append a second rule:

> For Chinese prose, borrow from ASD-STE100: consistent terms, explicit actors, and short, unambiguous sentences. Lead with the result, state facts and advice directly, and remove redundancy and self-evaluation.

Keep explanations that add a mechanism, causal distinction, or useful classification. Describe material uncertainty precisely in the claim. Avoid repeating a table in prose, speculating about the user's motives, or manufacturing criticism. A useful editing test: if removing a paragraph changes no fact, mechanism, condition, or decision, remove it.

[ASD-STE100](https://www.asd-ste100.org/STE_faq.html) is controlled English for technical documentation and was created to help non-native readers. For Chinese collaboration, borrow consistent terminology, explicit actors, and unambiguous sentences; do not import its English dictionary or claim STE compliance.

## Deployment

Inspect the existing global file, remove obsolete or repeated rules, and show the proposed result before writing. Ask only about unresolved choices. Back up the old file, apply the selected core and options once, and verify the read-back. Host-specific deployment does not authorize project edits, remote writes, commits, or publication.

For multiple hosts, compare the core and selected options separately. An unavailable host remains unverified; host inventories and private paths do not enter this repository.

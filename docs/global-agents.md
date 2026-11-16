# Host-Global AGENTS Guide

English | [中文](global-agents.zh-CN.md)

The [minimal core](../templates/AGENTS.global.md) keeps cross-task judgment, initiative, authorization boundaries, and stage records concise.

## Progressive project records

The global file routes meaningful project stages and explicit documentation or handoff requests to [`organized-proj`](../skills/organized-proj/SKILL.md); its procedure loads only when needed.

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

When selected, place the naming instruction first, followed by the collaborative opening, in the user's chosen language. Names are conversational preferences, not project attribution. Personal names and resolved host values stay out of the public template.

## On-demand development guides

These optional guides are ordinary Markdown files. Select the relevant guides once during global setup; no per-project installation or new Skill is needed.

| Guide | Read when | Focus |
| --- | --- | --- |
| [Coding and lint](../templates/optional/lint-toolchains.md) | Writing or changing code | Single responsibility, searchable names, no code comments, and project lint; defaults to clang-tidy/clang-format, Ruff, and Clippy/rustfmt. |
| [Backend](../templates/optional/guides/backend.md) | Backend or compiled algorithm work | Fast CMake/catkin/colcon iteration, bounded diagnostic logs, and independent interfaces. |
| [Frontend](../templates/optional/guides/frontend.md) | Designing or changing an interface | Information hierarchy, restrained presentation, interaction, and human visual acceptance. |
| [Review, commits, and pushes](../templates/optional/guides/git.md) | Code closeout, review, commits, or pushes | “收尾推送” runs full code simplification before publication; Git-only operations skip simplification. |

Copy only the selected language and guides to `guides/` beside the actual global `AGENTS.md`, using the canonical names `code.md`, `backend.md`, `frontend.md`, and `git.md`. Install the selected `lint-toolchains.md` or `lint-toolchains.zh-CN.md` as `code.md`; Chinese guide sources likewise use the canonical names when installed. Preserve local edits during updates. Inspect existing project conventions when applying a guide.

For the selected guides, the global file needs one routing line:

```markdown
- Read the relevant guide beside this file: coding → `guides/code.md`; backend or algorithms → `guides/backend.md`; interfaces → `guides/frontend.md`; review, simplification, or Git → `guides/git.md`.
```

Keep references only to installed guides. These are explicit instructions to read a file when needed; do not assume that an `@file.md` mention implements conditional loading. Keep the guide bodies out of the always-loaded core. Existing domain references under `templates/workspace/` remain optional; avoid installing overlapping UI instructions twice.

If `simplify-codebase` is selected, offer installation once when absent. The Git guide uses it when installed and works directly otherwise. See the [install prompt](../README.md#simplify-codebase).

When adopting `code.md`, move the selected coding and lint rules out of the always-loaded global file. Their behavior remains available for code work without loading it for unrelated queries.

## Concise, candid reporting

For this selected preference, replace the existing reporting line rather than append a second rule:

> Communicate naturally and directly with consistent terminology. Lead with the result and retain useful evidence and detail. State facts and unknowns plainly; label inferences and briefly explain their basis. Mention only limitations that affect judgment and avoid repetition. In instant messages, omit sentence-final periods.

Keep inference labels generic in public templates; a private configuration may use the user's selected assistant nickname. Select the sentence-punctuation preference independently; it applies to instant messages.

[ASD-STE100](https://www.asd-ste100.org/STE_faq.html) provides a reference for consistent terminology, explicit actors, and unambiguous sentences.

## Deployment

Compose the core and selected preferences by meaning: merge overlaps while preserving authorization boundaries and read triggers. Use a short opening and compact list unless the user prefers another format. Omit module headings, explanations, and examples; time-zone and guide-routing preferences need only one line each. Keep conditional procedures in the linked guides or Skills.

Inspect the existing global file, remove obsolete or repeated rules, and show the proposed result before writing. Ask only about unresolved choices. Back up the old file, apply the selected core and options once, and verify the read-back. Host-specific deployment does not authorize project edits, remote writes, commits, or publication.

For multiple hosts, compare the core and selected options separately. An unavailable host remains unverified; host inventories and private paths do not enter this repository.

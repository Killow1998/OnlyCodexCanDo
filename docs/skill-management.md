# Skill Selection Across Hosts

English | [中文](skill-management.zh-CN.md)

Unify sources, versions, and selection—not a large mandatory bundle on every computer. Make useful Skills available where they belong before adding automatic updates.

## Three different states

| State | Meaning | What it does not establish |
| --- | --- | --- |
| Installed | Files exist on disk | The current session discovers or uses them |
| Discoverable | Names, descriptions, and other metadata are candidates | Full instructions have been loaded |
| Used for this task | The agent reads instructions and uses relevant resources | Quality improved, or every script ran |

Codex already progressively loads Skills: metadata first, full instructions when selected. Large catalogs still have selection costs, and broad triggers can repeatedly load irrelevant procedures. Reducing discovery scope and narrowing triggers address different problems. [Official guidance](https://learn.chatgpt.com/docs/build-skills)

## Choose by purpose, not count

| Choice | Suitable use | Example |
| --- | --- | --- |
| Discoverable across projects | Broadly useful with precise triggers | Document formats or scoped official-documentation lookup |
| Project-scoped | Depends on a project, domain, or team convention | Simulation validation or framework-specific debugging |
| Explicit-only | Useful but substantially changes the working process | Deep interviews, TDD coaching, repository-wide refactoring review |
| Disabled for now | Conflicting rules, wrong triggers, missing dependencies, or uncertain benefit | A trial Skill awaiting revision and validation |

Recent non-use is not a reason to delete a rare but important capability. A large instruction file is also not automatically useless: check whether it is loaded and whether details can move into on-demand references.

## Three existing controls

### Disable without deleting

Current Codex supports disabling a local Skill by its actual instruction path in the user configuration; restart afterward:

```toml
[[skills.config]]
path = "/absolute/path/to/example-skill/SKILL.md"
enabled = false
```

Use the target host's real path and preserve existing configuration. Do not move an entire skill tree or delete plugin caches to implement a toggle. [Configuration](https://learn.chatgpt.com/docs/build-skills#enable-or-disable-local-codex-skills)

### Require explicit invocation

A maintained Skill can set this in its own `agents/openai.yaml`:

```yaml
policy:
  allow_implicit_invocation: false
```

Unlike disabling, this retains explicit invocation. Do not assume another agent's similar frontmatter field works in Codex; verify the installed version. Preserve provenance and local changes when modifying third-party Skills so updates do not erase them. [Invocation policy](https://learn.chatgpt.com/docs/build-skills#optional-metadata)

### Expose an entry only to selected projects

Keep source files in an ordinary directory outside automatic discovery, then symlink the selected Skill folder into a workspace's `.agents/skills/`. Codex follows symlinked Skill folders; the target must be readable on that host. Check symlink creation permissions on Windows. [Discovery locations](https://learn.chatgpt.com/docs/build-skills#where-to-save-skills)

A project link does not make a Skill project-only if it remains globally discoverable. Avoid exposing both an old copy and a new same-name entry; compare them before an approved migration. Absolute links are not portable across machines: public repositories should contain deployment instructions or genuinely portable relative sources.

## A bounded audit

1. **Inventory actual entries.** Inspect user, project, plugin, legacy locations, and disabled configuration. Record source, version or digest, invocation policy, and dependencies—not just a file count.
2. **Sample real tasks.** Separate root sessions, forks, and subagents. Disclose full versus partial reads. Deduplicate inherited history, distinguish forwarded agent prompts from direct user feedback, and check imported/replayed timestamps before assigning dates. A quoted blog or repeated instruction is not proof that an agent committed that failure. Mentions, quoted paths, and installation records are not successful-use evidence.
3. **Identify concrete costs.** Look for unnecessary questions, parallel planning documents, mandatory delegation, repeated verification, or reviews that turn into Issue publication, commits, or remote writes. Also record useful results.
4. **Give each candidate one disposition.** Keep, project-scope, explicit-only, revise, or disable, with reasons and unknowns. Recommendations alone do not justify installing everything.
5. **Validate a small selection.** Inspect the real catalog in a new session; check a matching task and a request that should not trigger it. Then compare rework and unnecessary artifacts in real use. Matching files establish synchronization, not effectiveness.

## Keep hosts consistent

Share sources and validated versions; privately record selected entries and local exceptions on each host. Prefer one source for the same task-specific Skill, but platform tools, domain modules, and personal names need not match. Validate on one host before updating others within authorization.

Compare local edits before syncing, then verify references, dependencies, and actual triggers. Upgrade when useful, not through a mandatory online check before every task. Do not synchronize all of `.codex`: sessions, credentials, databases, caches, and plugin runtime state are not Skill source. Update plugins through their manager, not by editing caches.

A source list and project links usually suffice for a few personal Skills. Consider plugin packaging when distributing to others or bundling connectors; do not build a new management platform merely to achieve consistency.

## Reusable read-only audit prompt

```text
Read-only audit this host's actual AGENTS.md, referenced rules, and selected Skills for contradictions or overlap that cause repeated questions, unintended stops, expanded scope, or incomplete delivery.
Check actual discovery scope and enabled state first. Sample representative sessions when available, disclose coverage, and do not equate installation or mentions with effective use.
Focus on autonomy, clarification, approval, completion, and verification stopping conditions. Distinguish intentional safeguards from accidental ceremony; do not ask again about unchanged decisions already authorized.
For each finding, provide the file and original instruction, likely effect, exact proposed replacement, and whether authority changes. Preserve explicit approval requirements; flag any proposed expansion separately without applying it.
Prioritize practical impact instead of a finding count. Separate useful rules from unproven concerns. Present reviewable suggestions before changing configuration, files, task titles, or external state. Keep private sessions and host details out of public repositories.
```

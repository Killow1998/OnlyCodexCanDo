---
name: codex-lfe
description: Configure, inspect, verify, or disable CodexLFE, which safely installs or validates canonical Codex Orchestration and routes bounded Executor work through a Luna Max Fast custom agent. Use when the user explicitly asks for CodexLFE setup, status, verification after restart, disable, repair guidance, Luna Fast Executor configuration, or migration of this setup to another PC.
---

# CodexLFE

CodexLFE is a thin lifecycle wrapper around canonical Codex Orchestration. Never copy, vendor, patch, or reimplement Orchestration. Use the bundled Nushell CLI for deterministic inspection and global-state changes.

## Locate the CLI

Resolve the plugin root as two directories above this `SKILL.md`, then use:

```text
nu <plugin-root>/scripts/codex-lfe.nu setup
nu <plugin-root>/scripts/codex-lfe.nu status
nu <plugin-root>/scripts/codex-lfe.nu disable
nu <plugin-root>/scripts/codex-lfe.nu verify
```

Do not read, print, request, or persist credentials. Do not substitute a repository-local script for the configurator found inside the installed canonical Orchestration plugin.

## Command workflow

### Status

Run `status` for read-only discovery. Report dependency provenance, managed-state health, and routing status separately. A missing setup is not authority to install or modify anything.

### Setup

Run `setup` only after the user explicitly asks for CodexLFE setup. The command prints its preview before applying. It must:

- accept only the enabled plugin ID `codex-orchestration@codex-orchestration` from `https://github.com/Cjbuilds/Codex-Orchestration.git`;
- stop on a same-name dependency from any other source;
- generate any Luna v2 shim from that machine's own `models_cache.json` and never from a bundled catalog;
- preserve unrelated config text and stop on ownership conflicts;
- create only the bounded `codex_lfe_executor` personal custom agent;
- invoke the installed canonical `configure_native_routing.py` preview before apply.

When setup succeeds, report `RESTART_REQUIRED`. Do not verify or spawn in the same task. Tell the user to fully quit Codex, reopen it, and create a new task.

### Verify

Run `verify` only in a new task after restart. Continue only when it returns `READY_FOR_SPAWN` and the callable agent tool exposes an exact custom-agent selector.

Spawn exactly `codex_lfe_executor` with `fork_turns = "none"` and this bounded, read-only packet:

```text
Return CODEX_LFE_ROUTE_ACCEPTED and nothing else. Do not edit files, call tools, contact other roles, or create descendants.
```

If the tool does not expose the exact custom-agent selector, report verification as unavailable; do not fall back to a direct model route. After a successful tool call, report only `route accepted` unless client metadata explicitly confirms the effective runtime model, provider, effort, and service tier. Child prose is not runtime evidence.

### Disable

Run `disable` only after an explicit request. It previews the canonical routing restoration, refuses drift, restores only CodexLFE-owned config bytes, removes only CodexLFE-created agent/catalog files, and retains canonical Codex Orchestration itself.

## Truthful states

- `RESTART_REQUIRED`: files and policy were written, but the current task cannot have loaded the agent.
- `READY_FOR_SPAWN`: static state, effective native policy, and shadowing checks passed; no child has run yet.
- `route accepted`: the current agent tool accepted the exact custom-agent route.
- `used and confirmed`: reserve for explicit runtime metadata.
- `RECOVERY_REQUIRED`: managed state is partial or drifted; stop instead of guessing.

Never claim that installing CodexLFE itself silently installed its dependency, that configuration hot-loaded the current task, or that a requested route actually ran without the required evidence.

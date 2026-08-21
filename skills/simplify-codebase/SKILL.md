---
name: simplify-codebase
description: Audit or simplify an existing codebase with evidence-backed deletions and consolidations while preserving intended behavior. Use when Codex is asked to reduce code bloat, dead code, duplication, defensive scaffolding, obsolete compatibility, unused abstractions or configuration, unnecessary tests, hand-rolled utilities, or general over-engineering; supports read-only audits, implementation, and review of proposed simplifications. Do not use for formatting-only cleanup, an unauthorized product redesign, or weakening authentication, data safety, irreversible-operation, or release controls without explicit evidence and authority.
---

# Simplify a Codebase

Turn a broad cleanup request into a bounded set of high-confidence simplifications. Optimize total states, dependencies, failure modes, and maintenance obligations, not line count alone.

## Choose the operating mode

- Use **audit** mode when the user asks to find, assess, or propose simplifications. Make no repository writes.
- Use **implementation** mode when the user asks to simplify, refactor, or fix the code. Apply only candidates supported by the requested scope and evidence.
- Use **review** mode for an existing diff or proposal. Check whether it truly removes complexity and preserves the required behavior.
- Preserve the user's authorization boundary. A cleanup request does not authorize dependency changes, compatibility breaks, data migrations, publication, or removal of existing safety controls unless those actions are clearly in scope.

## Establish the behavior boundary

1. Read the applicable `AGENTS.md`, project documentation, package manifests, and relevant design records.
2. Inspect the current branch and working tree before writes. Preserve unrelated changes.
3. Identify the production corpus, non-production corpus, generated surfaces, dynamic loaders, and real acceptance commands for the area in scope.
4. State the behavior and compatibility that must remain. Ask only if an unresolved choice would materially change architecture, public behavior, data, security, or authorization.

Do not create a hash, frozen contract, baseline, gate, shadow state, bespoke validator, or extra compatibility path merely to prepare for simplification. Add one only after naming the concrete failure it prevents and why Git, versions, keys, transactions, uniqueness, types, or ordinary targeted tests are insufficient.

## Survey high-leverage surfaces

Start with production code that carries meaningful ownership or lifecycle complexity, not with cosmetic issues. Use `rg` for exact symbols, wire strings, configuration keys, event names, constructors, and both direct and indirect call forms; then read every material call site. Check registries, reflection, generated code, plugin loading, scripts, examples, and serialization before declaring something unused.

Look for:

- public surfaces with no production consumer;
- duplicate representations or mirrored state;
- speculative adapters, extension points, configuration, compatibility, or rollback paths;
- defensive copies, freezes, validators, sentinels, readiness flags, caches, and gates that protect no demonstrated trust or lifecycle boundary;
- wrappers, packages, and layers that relocate rather than remove complexity;
- hand-rolled infrastructure that a maintained dependency or runtime builtin could replace with net deletion; and
- tests or documentation that are the only consumers of behavior no longer required.

Treat file length, cyclomatic complexity, nesting depth, and dependency count as survey signals, not universal gates. A hard threshold is useful only when the project already owns it as an explicit constraint and the change lowers total complexity instead of splitting one responsibility across more wrappers.

Read [references/candidate-evidence.md](references/candidate-evidence.md) when the survey finds several candidate classes or when a trust, lifecycle, dependency, or compatibility decision is not obvious.

## Prove or reject each candidate

For each candidate, record:

1. The exact surface and its current responsibility.
2. Production, non-production, generated, and ambiguous consumers.
3. The behavior change, including what is deliberately given up.
4. Net reduction: code, states, dependencies, tests, documentation, and operational paths removed minus replacement glue.
5. Risk, rollback or migration needs, and the smallest real verification surface.

Reject or downgrade a candidate when a production consumer exists and deletion would be an unauthorized feature decision; when an existing safety or compatibility measure has a concrete failure case the new evidence does not beat; when churn exceeds the removed obligation; or when the claim rests only on file size, a linter, an unused-symbol tool, or aesthetic dislike.

Prefer a direct function or module for a single current path. An interface, factory, adapter, provider, registry, strategy, or manager needs at least two real consumers or a demonstrated process, ownership, dependency, or release boundary. Do not add an adjacent feature, future extension point, or explanatory scaffold that the user did not request.

Prefer a few well-proven candidates over a long backlog of guesses. Do not scatter speculative TODO comments as a substitute for evidence.

## Audit defensive machinery precisely

For each copy, freeze, runtime validator, hash, baseline, gate, retry layer, rollback path, or lifecycle flag, name:

- where the value or event originates;
- which boundary changes trust or ownership;
- the concrete accident the mechanism prevents;
- why existing language, storage, transaction, version-control, and test guarantees do not cover it; and
- the cost and failure modes introduced by the mechanism itself.

Typed same-process calls usually do not need hostile-input defenses. Parser, configuration, model/tool JSON, durable storage, queue, worker, process, network, authentication, data-safety, irreversible-operation, and release boundaries may. Do not remove an existing control merely because it would fail the bar for a new control; inspect its history and risk first.

## Implement the smallest coherent reduction

1. Rank candidates by confidence and net obligation removed, then select only the number needed for the requested scope.
2. Remove or consolidate the owning code and all now-obsolete callers, tests, configuration, documentation, generated inventories, and compatibility branches together.
3. Preserve a dependency only when it is still used. Add a dependency only when the remaining wrapper is materially smaller and the package's maintenance, footprint, and behavior fit the project.
4. Keep comments that explain non-obvious surviving constraints; remove comments that only narrate deleted mechanics or obvious code.
5. Do not widen the task into unrelated style cleanup or architecture renovation.
6. When removing unrequested or speculative work, remove its narrative residue too. Names, comments, tests, commits, and pull-request summaries should describe the behavior delivered, not advertise unrelated features that were never required.

## Verify and stop

- Run the smallest targeted checks that exercise the real behavior plus one relevant boundary or independent corroboration. Inspect the final diff.
- Update or remove obsolete tests when behavior intentionally disappears; tests are evidence, not permanent product requirements.
- If three meaningful attempts expose the same unresolved problem, stop editing and review the responsibility, data flow, or architecture.
- Stop after one complete survey of the requested scope and implementation or reporting of the selected candidates. Do not rescan indefinitely, invent new gates, or polish already-accepted code merely because time remains.

## Report the result

Report:

- implemented or proposed simplifications and the evidence for each;
- behavior intentionally preserved or removed;
- net code, state, dependency, or maintenance obligations removed;
- checks run on the real acceptance surface; and
- only material rejected candidates that affected the decision, plus remaining uncertainty or decisions that still require the user. Do not turn the report into a catalog of unrelated things not added.

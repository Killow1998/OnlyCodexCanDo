---
name: simplify-codebase
description: Review or implement code simplification, structural refactoring, or explicit code closeout, including “代码收尾” and “收尾推送”. Use for code bloat, repeated validation, needless wrappers, coupled modules, comments, or implementation-coupled tests. Git-only commits or pushes, documentation closeout, and formatting-only edits do not trigger a cleanup pass.
---

# Simplify a Codebase

Reduce maintenance obligations, not line count alone.

## Scope

- **Audit:** propose simplifications without edits. **Implementation:** apply requested simplifications. **Review:** assess an existing diff.
- Explicit code closeout implements the full reduction below across the current codebase within existing functionality. “收尾推送” includes that work before committing and pushing; use the applicable Git guide for publication.
- Lock the requested behavior and acceptance scope. Inspect the current diff and relevant callers; preserve unrelated work and required compatibility.
- Reuse existing project decisions and evidence. Ask only about unresolved product or architecture choices.
- Simplification does not itself authorize publication, data migration, compatibility breaks, or removal of required security controls.

## Decide what earns its place

Trace the affected data and control flow across module boundaries. Start with duplicated state, costly dependencies, unused surfaces, and pass-through layers. Check actual callers and relevant dynamic or external consumers before declaring code unused.

Use the **deletion test**: does removing a layer eliminate complexity or spread it into callers? Prefer removal in the first case and preserve the responsibility in the second. If the user requests ablation experiments, compare the relevant before/after behavior; do not invent an experiment for every candidate by default.

Prefer deep modules with small interfaces that localize changes. Inline single-use forwarding with no independent responsibility. Split a heavy module by cohesive responsibilities, not a line quota; extra files or wrappers do not demonstrate decoupling.

Scope a fix by its root cause and affected responsibilities, not the smallest diff. Replace related workarounds when a coherent repair is needed across modules; explain broad changes before implementation.

Establish what obligation disappears and what behavior remains. Read [candidate evidence](references/candidate-evidence.md) only for an unresolved consumer, boundary, comment-removal, or testing question. Understand an existing safeguard's actual failure case before removal.

## Make the coherent reduction

- Remove or consolidate the implementation together with obsolete callers, tests, configuration, and documentation.
- Establish types at external boundaries; remove internal checks already covered by that contract. Keep checks where the guarantee can change.
- Keep error handlers that own recovery, boundary translation, or cleanup. Remove redundant rethrows and repeated logging; preserve failures instead of masking them as success.
- Prefer existing language and platform facilities; adopt a maintained dependency when it reduces total ownership cost.
- Keep useful behavior covered; replace implementation-coupled assertions rather than stacking another test layer. An assertion must distinguish the required result from a plausible wrong result.
- Remove all code comments in scope, including explanatory comments and commented-out code; do not add replacement comments. Express intent through names and structure, and move necessary rationale to existing project documentation.

## Verify and finish

Follow the agreed acceptance method, preferring focused existing E2E checks through the requested entry and actual configuration. Add checks only for an uncovered consequential risk within that method.

Reuse valid evidence; investigate changed behavior or unresolved failures without weakening correct expectations. Inspect the diff and stop when the requested reduction has adequate evidence.

Report the change, the obligation removed, verification, and material uncertainty. No per-candidate dossier or fixed number of attempts is required.

Design reference: [codebase-design](https://github.com/mattpocock/skills/blob/main/skills/engineering/codebase-design/SKILL.md).

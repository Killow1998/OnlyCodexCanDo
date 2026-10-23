---
name: simplify-codebase
description: Audit, review, or simplify an existing codebase by removing unnecessary code, state, dependencies, and abstractions while preserving required behavior. Use for code bloat and over-engineering, not formatting-only cleanup.
---

# Simplify a Codebase

Reduce maintenance obligations, not line count alone.

## Scope

- **Audit:** propose simplifications without edits. **Implementation:** apply requested simplifications. **Review:** assess an existing diff.
- Inspect the working tree and the affected behavior and callers. Preserve unrelated work and required compatibility; ask only about unresolved product or architectural decisions.
- Simplification does not itself authorize publication, data migration, compatibility breaks, or removal of required security controls.

## Decide what earns its place

Start with the requested area and its costly dependencies, duplicated state, unused surfaces, or pass-through layers. Check actual callers and relevant dynamic or external consumers before declaring code unused.

Use the **deletion test** as a design question: if removing a layer makes complexity disappear, it may be redundant; if that complexity spreads into callers, the layer is doing useful work. This is a reasoning aid, not a requirement to delete working code as an experiment.

Prefer deep modules with small interfaces that contain complexity and localize changes. Keep an adapter or abstraction when current variation or a real ownership, process, or dependency boundary warrants it. File size alone does not justify splitting a responsibility.

For a candidate, establish what obligation disappears and what required behavior remains. Investigate further only where consumer, trust, lifecycle, or compatibility evidence is unclear; use [candidate evidence](references/candidate-evidence.md) for those cases. An existing safeguard needs its actual failure case understood before removal.

## Make the coherent reduction

- Remove or consolidate the implementation together with obsolete callers, tests, configuration, and documentation.
- Prefer existing language and platform facilities; adopt a maintained dependency when it reduces total ownership cost.
- Keep useful interface behavior covered. Replace implementation-coupled tests with behavior checks where needed, instead of stacking another test layer.
- Keep comments for intent and constraints the code does not express; remove code restatements, stale explanations, change-history logs, and unnecessary location markers. Preserve license notices and tool-required comments.

## Verify and finish

Use the smallest existing check that can expose a relevant behavioral regression, through the public interface where practical. Remove tests for intentionally removed behavior; add checks only for an uncovered consequential risk.

If checks fail, investigate the cause rather than adding compensating gates. Inspect the diff and stop once the requested reduction has adequate evidence.

Report the change, the obligation removed, verification, and material uncertainty. No per-candidate dossier or fixed number of attempts is required.

Design reference: [codebase-design](https://github.com/mattpocock/skills/blob/main/skills/engineering/codebase-design/SKILL.md).

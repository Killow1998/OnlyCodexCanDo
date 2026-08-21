# Simplification Candidate Evidence

Use this reference only when a candidate needs more than the core workflow.

## Consumer classes

| Class | Typical evidence | Consequence |
| --- | --- | --- |
| Production | Runtime calls, loaders, manifests, wire values, persisted formats, deployed scripts | Removal is a behavior decision unless the consumer is removed in the same authorized change. |
| Non-production | Tests, docs, snapshots, examples, comments | May reveal intended behavior, but does not alone prove a live requirement. |
| Generated | Schemas, catalogs, bindings, compiled or generated sources | Trace the generator and source of truth before editing or deleting. |
| Ambiguous | Examples used as smoke tests, migration tools, operational scripts, reflective names | Inspect how the project ships and verifies them before classifying. |

## Strong candidate patterns

### Unused public surface

Prove that no production, dynamic, wire, or external consumer remains. Remove the implementation, export, documentation, tests that only pin it, and any compatibility promise together.

### Duplicate source of truth

Map writers, readers, synchronization, and failure behavior for both representations. Prefer one owner when the second value can be derived cheaply and does not provide an independent durability or trust boundary.

### Speculative generality

Look for adapters with one implementation, configuration with one valid value, registries with no runtime mutation, extension points with no consumer, and compatibility for versions that never shipped. Keep them only when a current consumer or explicit supported future commitment exists.

### Defensive scaffolding

Draw the trust and ownership path. Several sentinels, readiness promises, copies, caches, or terminal-state flags may mirror one lifecycle fact. Consolidate only after preserving distinct publication, cancellation, rollback, containment, or ownership transitions that have real failure cases.

### Hand-rolled infrastructure

Compare the exact covered semantics, runtime support floor, dependency health, transitive footprint, and remaining wrapper. Count implementation, dedicated tests, and documentation removed. A package that merely moves the same complexity is not a simplification.

### Layer or package indirection

Identify the independent responsibility, release boundary, dependency direction, or ownership that justifies the layer. Merge it when it has no separate evolution or consumer and the merge reduces public surface rather than only file count.

## Weak evidence

Do not approve a candidate from any one of these alone:

- a large file or high line count;
- a static unused-symbol report without dynamic-path review;
- duplication percentage without semantic comparison;
- tests being difficult to maintain;
- a newer library existing;
- a preference for fewer files; or
- "this looks over-engineered."

## Candidate decision record

Use a compact table when several candidates exist:

| Candidate | Production consumers | Behavior delta | Net reduction | Risk and verification | Decision |
| --- | --- | --- | --- | --- | --- |
| Exact symbol or surface | Calls or none, with evidence | Preserved or deliberately changed | Removed obligations minus glue | Concrete boundary and check | Implement, propose, reject |

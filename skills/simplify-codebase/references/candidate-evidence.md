# Simplification Candidate Evidence

Read only the section relevant to an unresolved consumer, trust, lifecycle, dependency, compatibility, or comment-removal question.

## Required comment removal

Implementation leaves the requested scope free of code comments, including explanations of intent or constraints. This is a required result, not a judgment about whether a comment is redundant. Use language-aware edits to preserve comment markers inside string data. Move necessary rationale and notices into appropriate project documentation; replace functional directives with equivalent code or configuration. If removal conflicts with required behavior, report that concrete conflict as unfinished work instead of retaining comments and claiming completion.

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

Trace the trust and ownership path, the concrete failure prevented, and what existing guarantees already cover. Several sentinels, readiness promises, copies, caches, or terminal-state flags may mirror one lifecycle fact. Preserve distinct publication, cancellation, rollback, containment, or ownership transitions that have real failure cases.

For repeated validation, identify where an invariant is established and where it can become false. Rechecking the same immutable typed value in each internal layer is a candidate; checking a changed authorization, concurrent state, or new external input is a separate responsibility. A hypothetical failure alone does not justify new defensive infrastructure.

For exception handling, identify the recovery, boundary translation, or cleanup each handler owns. Merge handlers that only repeat logging or rethrow unchanged errors. Preserve the original cause; returning an empty value or success after failure may change behavior rather than simplify it.

### Implementation-coupled tests

Ask which incorrect user-visible result an assertion rejects. Internal call counts, private structure, source-string matches, and duplicate happy paths often miss real defects or break on a behavior-preserving refactor. Keep contractual protocol or generated-format assertions where the representation itself is the public behavior.

Reuse the existing behavior check before adding another. A relevant existing failure or a representative wrong-result comparison can show that it detects a regression; do not require a mutation campaign for every test. Keep mandatory release checks and follow the user's agreed acceptance method.

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

Record only evidence that changes the decision or is needed to review the result. Use a comparison table when it helps choose among candidates.

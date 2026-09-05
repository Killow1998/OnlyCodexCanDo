# Simplify Codebase Evaluation

English | [中文](simplify-codebase-evaluation.zh-CN.md)

## Target and boundary

- Target: [`devxsameer/blog-api`](https://github.com/devxsameer/blog-api) at `72f22d3ee2be` (2026-01-20).
- Rationale: the repository describes itself as intentionally over-engineered, while still containing real authentication, authorization, database, transaction, and API boundaries.
- Size: 5,154 maintained text lines in 109 files after excluding the lockfile and generated Drizzle metadata; the production TypeScript corpus contained 3,814 lines in 85 files.
- Behavior boundary: preserve API behavior, token lengths and SHA-256 digests, error-to-status mappings, database transactions, authentication safeguards, and public route contracts. No dependency, schema, or product change was authorized.

The modified copy remained local and was not committed or published to the target repository.

## One bounded pass

The Skill selected only high-confidence candidates:

- removed one duplicate email-token utility module by sharing the existing random-token and SHA-256 implementation with explicit byte lengths;
- bypassed service functions that only forwarded tag queries to the repository while retaining tag normalization as real business logic;
- consolidated duplicate API-error response branches;
- removed unused error state, database error fields, path setup, imports, and callback names; and
- retained controller/service/repository layers where they still owned authorization, transactions, aggregation, or persistence behavior.

No authentication hash was removed. Password hashing protects stored credentials, and refresh/email token hashing limits direct replay after database disclosure. Types, Git, and ordinary tests do not provide those security properties.

## Measured result

| Metric | Before | After | Delta |
| --- | ---: | ---: | ---: |
| TypeScript files | 85 | 84 | -1 |
| TypeScript physical lines | 3,814 | 3,768 | -46 (-1.2%) |
| TypeScript nonblank lines | 3,259 | 3,218 | -41 |
| Branch keywords (`if`, `else`, `switch`, `case`, `catch`, `for`, `while`) | 98 | 97 | -1 |
| Dependencies | unchanged | unchanged | 0 |

The modest reduction is the result: the Skill stopped after removing proven duplication and indirection instead of flattening security and persistence boundaries to chase a larger percentage.

## Verification and limitations

Passed checks:

- TypeScript build and `--noUnusedLocals --noUnusedParameters`;
- compiled behavior checks for 128-character refresh tokens, 64-character email tokens, and stable SHA-256 output;
- compiled boundary checks for validation, known API, PostgreSQL uniqueness, and unknown-error responses (400/404/409/500); and
- `git diff --check` plus final diff inspection.

The repository's 12 Vitest integration tests could start only outside the sandbox, then all stopped in database setup because no PostgreSQL test database was available. Therefore this evaluation does not claim full integration-test success. A future evaluation should repeat the same patch against a disposable PostgreSQL instance and add an independent sample containing a demonstrably unnecessary hash or gate; this run proves hash retention at a real security boundary, not removal of a meaningless hash.

## Rule changes derived from the evaluation

- Code size and cyclomatic complexity are triage signals, not universal gates.
- Single-path interfaces, factories, adapters, providers, registries, strategies, and managers need a real second consumer or a demonstrated boundary.
- Implement only requested behavior; do not add adjacent features or preserve explanations of irrelevant omissions in code or pull-request prose.
- Report only material rejected candidates. A cleanup report should not become a catalog of things that were never requested.

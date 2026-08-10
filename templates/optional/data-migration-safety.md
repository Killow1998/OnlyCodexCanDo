## Data Migration Safety

Select this module when the agent may change schemas or persistent data.

- Before schema changes, migrations, data deletion, backfills, or data moves, explain the affected data, failure risk, rollback path, and verification plan.
- Resolve exact targets before writing. Back up or use a reversible migration when the failure cost warrants it.
- Verify both the migrated result and the behavior of an important consumer; a successful migration command alone is not acceptance evidence.

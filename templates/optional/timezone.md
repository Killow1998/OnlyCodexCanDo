## Recorded Time Zone

Before merging this module, replace `<IANA_TIME_ZONE>` with the user-selected IANA time zone. Do not install the unresolved placeholder.

- Use `<IANA_TIME_ZONE>` explicitly for agent-created worklogs, experiment records, and handoff timestamps even when the host system uses another time zone.
- Preserve source timestamps when quoting external evidence, and label conversions rather than silently rewriting them.

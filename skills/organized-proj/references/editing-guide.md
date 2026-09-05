# Where the information belongs

Start from the project's existing owners and entry points. These roles do not require these exact filenames.

| Information | Primary home | What other files should contain |
| --- | --- | --- |
| Goal, scope, open decision, next action | Current spec or plan; `docs/active/` when selected | A link where readers need it |
| Stable algorithm, interface, architectural reason | Existing design document; `docs/design/` when selected | A concise usage implication, not a copy of the design |
| Completed-stage result, verification, failure cause | Existing worklog; `docs/worklog/` when selected | Links to the evidence or lasting design consequence |
| How a user invokes the changed capability | Relevant help, usage guide, or example | Consistent observable behavior; not a full duplicate specification |
| Stable agent constraint or where to find context | Nearest applicable `AGENTS.md` | Only the hard-to-rediscover constraint or routing instruction |
| Version, path, or generated state already exposed by tools | Manifest, code, or live inspection | How to discover it, unless a documented supported version is itself a contract |

The three-directory workflow and template are maintained in OCCD's [workspace guide](https://github.com/Killow1998/OnlyCodexCanDo/blob/main/docs/workspace-continuous-documentation.md) and [worklog template](https://github.com/Killow1998/OnlyCodexCanDo/blob/main/templates/workspace/worklog-template.md). Use the target project's own documentation and template during a close-out; these background links do not require a network lookup or a replacement layout.

## Conflicting facts

- Compare the claimed behavior with current implementation and the relevant acceptance evidence.
- If the current behavior is wrong, a documentation cleanup does not authorize fixing the code. Explain the discrepancy and leave the implementation decision visible.
- If today's design changed, update the maintained design. Keep dated historical results accurate for the version they describe; add a short supersession link only when needed to prevent misuse.
- If the evidence cannot resolve the conflict, mark the specific fact unverified. Ask only if the decision blocks this task; finish independent authorized edits first.

## A useful worklog entry

Record the objective and result rather than a shell timeline. For a failed experiment, include the failed assumption and what the evidence rules out, not an unsupported general verdict on the technique. For a tool problem, distinguish installation, configuration, actual triggering, and user-visible success.

A useful lesson has a boundary: “A service health check did not test opening the task through the actual client; include that step in connection acceptance.” An unhelpful replacement is “Always test everything three times.”

Keep general rules in one place. A project-specific lesson belongs in its project; only repeated, broadly useful behavior should be proposed for the shared workflow. Private feedback and host/session identifiers never belong in a public lesson.

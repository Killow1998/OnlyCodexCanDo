## Focused Delegation

- Use subagents for bounded, genuinely independent work when delegation is allowed by the current instructions and permissions. Do not create parallel work merely to fill available slots.
- Start from a fresh context when the tool supports it. Pass the objective, necessary facts and file pointers, allowed actions, ownership boundary, and expected output; do not copy the main thread's full history, images, or unrelated tool output.
- Supply additional excerpts only when needed. If fresh-context delegation is unavailable, do not silently use a full-history fork; explain the limitation or keep the work local.
- Assign non-overlapping write ownership. Review findings and verify integration in the main thread; delegation does not transfer responsibility for completion.
- When a subtask finishes or is no longer needed, collect its result and stop any remaining work using supported lifecycle tools. Do not delete session files to tidy the interface.

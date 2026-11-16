# Review, Commits, and Pushes

Read for review, simplification, code closeout, commits, or pushes. Explicit code closeout, including “代码收尾” and “收尾推送”, requests the full reduction below; “收尾推送” then commits and pushes. Review-only requests produce findings. Git-only commit or push requests go directly to the final section.

## Code closeout, simplification, and review

Enter code closeout and global refactoring: deeply simplify and restructure the current codebase within its existing functionality. Add no features; focus on reducing code, decoupling responsibilities, and improving architecture.

Remove meaningless repeated null checks and defensive boundary checks. Before introducing complex logic for hypothetical low-probability concurrency or security scenarios, agree with the user on the concrete risk, likelihood, and code cost. Validate external input at the system entry and convert it to definite types; trust that contract internally and remove repeated validation. Use ablation experiments to remove meaningless abstractions and designs. Inline logic used only once when it has no independent complexity; avoid unnecessary try/catch blocks and function splitting. Delete outdated comments, abandoned code, and redundant explanations so the code explains itself and reflects the current design.

Review data and control flow across the codebase and fix structural causes rather than local symptoms. Preserve readability and extensibility, clarify module boundaries, and remove implicit coupling so changing or adding a module does not require system-wide debugging. Reduce file length by separating cohesive responsibilities in overloaded files. Remove brittle, meaningless tests; prefer concise E2E checks of core functionality.

Use `simplify-codebase` when installed for this simplification or review; otherwise follow this section directly.

## Commit and push

- Inspect the staged diff for unrelated edits, credentials, and temporary artifacts.
- Review READMEs affected by this task: foreground the project's purpose, core capabilities, and getting-started path; place work records and maintenance instructions in the appropriate documents and update stale status.
- Group commits by intent. Follow repository conventions and explain what changed and why.
- Use the authorized branch and remote. Review alone does not authorize a push. Force-pushing or rewriting shared history requires matching authority; existing authorization remains valid within its scope.

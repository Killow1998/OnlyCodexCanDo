# Review, Commits, and Pushes

Read for review, simplification, commit, or push work. A review-only request produces findings; a simplification request authorizes code changes. Ordinary commits and pushes go directly to the final section.

## Requested simplification and review

Optimize the code as a whole rather than settling for locally optimal improvements. Perform ablation experiments to remove meaningless abstractions, designs, and tests. Preserve readability and extensibility, strengthen modularity, and eliminate the need to debug the entire system whenever a module is changed or added. Add no new features at this stage; focus on code optimization and reduce the length of individual source files where possible. E2E tests are recommended to confirm functional completeness.

## Commit and push

- Inspect the staged diff for unrelated edits, credentials, and temporary artifacts.
- Group commits by intent. Follow repository conventions and explain what changed and why.
- Use the authorized branch and remote. Review alone does not authorize a push. Force-pushing or rewriting shared history requires matching authority; existing authorization remains valid within its scope.

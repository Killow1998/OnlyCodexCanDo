## Windows Shell and Environment

Apply this section only when the agent is running in Windows native. Do not copy it into Linux, macOS, or ordinary WSL environments.

- When shell behavior affects the task, confirm Windows native versus WSL and report the PowerShell executable and version actually used.
- Prefer an available `pwsh -NoProfile` for PowerShell-native built-ins and short deterministic checks. Use Windows PowerShell 5.1 only when required or when `pwsh` cannot run.
- Do not assume a standard `pwsh` installation path. Resolve the executable that actually starts; WindowsApps aliases may exist without being runnable in the current sandbox.
- Keep filesystem mutations in one shell end to end. Avoid fragile nesting across PowerShell, `cmd`, Git Bash, and WSL.
- Use `-LiteralPath` for user-controlled paths, spaces, brackets, and other special characters. Check `$LASTEXITCODE` after external programs and preserve `stderr` when diagnosing failures.
- After a failure, classify the cause and change the next attempt. Do not repeat the same command blindly.
- Move complex reusable PowerShell logic into a scoped `.ps1`. Remove task-created temporary scripts before finishing unless they become maintained project tooling.
- Use Git Bash or WSL for genuinely Unix-first projects when that reduces translation risk; do not mix shells merely by habit.

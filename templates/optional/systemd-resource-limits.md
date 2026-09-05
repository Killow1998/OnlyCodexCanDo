## Linux systemd Resource Limits

- Agree on limits with the user instead of inventing fixed values.
- For memory-intensive training, simulation, evaluation, conversion, indexing, or serving, prefer a `systemd-run --user` scope or named service with explicit `MemoryMax` and `MemorySwapMax` values that leave headroom for the OS and interactive work.
- Record the selected limits for real experiments. Do not claim that a limit is safe without checking host memory and the workload's expected peak.

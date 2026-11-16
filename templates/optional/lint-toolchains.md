# Coding and Lint

Read when writing or changing code. Follow existing project conventions.

- Follow the single-responsibility principle, use searchable names, and add no code comments.
- Prevent corrected errors through structure or types first; enforce remaining statically detectable patterns with existing project lint rules, not unit tests. Reuse actionable rules before adding custom checks.
- For C++ development, default to clang-tidy/clang-format; for Python, Ruff; for Rust, Clippy/rustfmt. Reuse the project's toolchain and configuration. When tools or configuration are missing, install and configure them within the project's version constraints and integrate them into its check entry.

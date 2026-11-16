import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def check(source: Path, root: Path, env: dict[str, str], expected: int, *arguments: str) -> None:
    result = subprocess.run(
        [sys.executable, "-B", str(source / "scripts/check.py"), *arguments],
        cwd=root,
        env=env,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )
    if result.returncode != expected:
        raise RuntimeError(f"{source.name} {arguments}: expected exit {expected}, got {result.returncode}\n{result.stdout}\n{result.stderr}")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    skills = sorted(path.parent.parent for path in (root / "skills").glob("*/scripts/check.py"))
    with tempfile.TemporaryDirectory(prefix="occd-release-") as temporary:
        codex_home = Path(temporary) / ".codex"
        env = dict(
            os.environ,
            CODEX_HOME=str(codex_home),
            PYTHONUTF8="1",
            PYTHONDONTWRITEBYTECODE="1",
        )
        for source in skills:
            installed = codex_home / "skills" / source.name

            check(source, root, env, 1, "--check-global")
            check(source, root, env, 1, "--global-skill", str(installed))
            check(source, root, env, 2, "--check-global", "--skip-global")
            if installed.exists():
                raise RuntimeError(f"Check unexpectedly created {installed}")
            shutil.copytree(source, installed)
            check(source, root, env, 0, "--check-global")
            skill_file = installed / "SKILL.md"
            changed = skill_file.read_bytes() + b"\nLocal installation change\n"
            skill_file.write_bytes(changed)
            check(source, root, env, 0)
            check(source, root, env, 1, "--check-global")
            check(source, root, env, 1, "--global-skill", str(installed))
            if skill_file.read_bytes() != changed:
                raise RuntimeError(f"Check modified installed source: {source.name}")
            print(f"[ok] {source.name}: source-only default; explicit installed checks; no deployment")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

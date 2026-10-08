import subprocess
from pathlib import Path


def run_git_command(repo_path: Path, args: list[str]) -> str:
    """Run a Git command inside the repository."""

    result = subprocess.run(
        ["git", *args],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )

    return result.stdout.strip()


def get_recent_commits(repo_path: Path, limit: int = 5) -> list[str]:
    """Return the most recent commits."""

    output = run_git_command(
        repo_path,
        ["log", f"-{limit}", "--oneline"],
    )

    return output.splitlines()


def get_commit_diff(repo_path: Path, commit_hash: str) -> str:
    """Return the changes introduced by a commit."""

    return run_git_command(
        repo_path,
        ["show", "--format=", commit_hash],
    )
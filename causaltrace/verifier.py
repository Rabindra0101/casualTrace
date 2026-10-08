
import subprocess
import sys
import tempfile
from pathlib import Path


def run_command(args, cwd):
    return subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )


def test_commit(repo_path: Path, commit: str, test_directory: str):
    """Run pytest at a commit in an isolated Git worktree."""

    with tempfile.TemporaryDirectory(prefix="causaltrace-") as temp:
        worktree = Path(temp) / "repo"

        run_command(
            ["git", "worktree", "add", "--detach",
             str(worktree), commit],
            repo_path,
        )

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "-v"],
                cwd=worktree / test_directory,
                capture_output=True,
                text=True,
            )

            return {
                "commit": commit,
                "passed": result.returncode == 0,
                "return_code": result.returncode,
                "output": result.stdout + "\n" + result.stderr,
            }

        finally:
            run_command(
                ["git", "worktree", "remove", "--force",
                 str(worktree)],
                repo_path,
            )


def verify_regression(repo_path: Path, suspect_commit: str):
    """Compare a suspected regression commit with its parent."""

    parent_commit = f"{suspect_commit}^"
    test_directory = "demo/sample_repo"

    print("\n[5] Running counterfactual verification...\n")

    before = test_commit(repo_path, parent_commit, test_directory)
    after = test_commit(repo_path, suspect_commit, test_directory)

    print(f"Parent commit: {parent_commit}")
    print(f"Result: {'PASS' if before['passed'] else 'NOT PASS'}")

    print(f"\nSuspect commit: {suspect_commit}")
    print(f"Result: {'PASS' if after['passed'] else 'NOT PASS'}")

    verified = (
        before["return_code"] == 0
        and after["return_code"] == 1
        and "FAILED" in after["output"]
    )

    print("\n" + "=" * 60)

    if verified:
        print("COUNTERFACTUAL EVIDENCE FOUND")
        print("Parent version: PASS")
        print("Suspected version: FAIL")
        print("Regression introduced between these revisions.")
    else:
        print("REGRESSION NOT VERIFIED")
        print("Inspect test output and execution errors.")

    return verified

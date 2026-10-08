
import subprocess
import sys
from pathlib import Path


def run_pytest(repo_path: Path) -> dict:
    """Run pytest using the active Python interpreter."""

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-v"],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )

    output = result.stdout + "\n" + result.stderr

    # pytest exit code 1 means tests ran and at least one failed.
    # Other nonzero codes can indicate configuration, collection,
    # missing dependencies, or other execution problems.
    return {
        "passed": result.returncode == 0,
        "test_failed": result.returncode == 1,
        "execution_error": result.returncode not in (0, 1),
        "return_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "output": output,
    }

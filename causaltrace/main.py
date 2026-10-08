
from pathlib import Path

from causaltrace.git_analyzer import (
    get_commit_diff,
    get_recent_commits,
)
from causaltrace.test_runner import run_pytest
from causaltrace.nemotron_client import generate_root_cause_hypothesis
from causaltrace.verifier import verify_regression


def main():
    project_root = Path(__file__).resolve().parent.parent
    target_repo = project_root / "demo" / "sample_repo"

    print("\nCAUSALTRACE")
    print("=" * 60)

    # 1. Reproduce the failure
    print("\n[1] Reproducing failure...\n")

    test_result = run_pytest(target_repo)

    if test_result["execution_error"]:
        print("STATUS: TEST EXECUTION ERROR")
        print(test_result["output"])
        return

    if test_result["passed"]:
        print("STATUS: PASS")
        print("No regression detected.")
        return

    print("STATUS: FAIL")
    print("\nFailure output:")
    print(test_result["output"])

    # 2. Inspect Git history
    print("\n[2] Inspecting Git history...\n")

    commits = get_recent_commits(project_root)

    if not commits:
        print("No commits found.")
        return

    for commit in commits:
        print(commit)

    # 3. Inspect latest change
    latest_commit = commits[0]
    commit_hash = latest_commit.split()[0]

    print("\n[3] Examining latest change...\n")

    diff = get_commit_diff(project_root, commit_hash)
    print(diff)

    # 4. Generate an AI hypothesis
    print("\n[4] Asking NVIDIA Nemotron to analyze the evidence...\n")

    hypothesis = generate_root_cause_hypothesis(
        test_output=test_result["output"],
        git_diff=diff,
    )

    print("NEMOTRON ROOT-CAUSE HYPOTHESIS:")
    print(hypothesis)
    print("\nVerification status: NOT YET VERIFIED")

    # 5. Verify the candidate commit
    print("\nStarting counterfactual experiment...")

    verified = verify_regression(project_root, commit_hash)

    if verified:
        verification_status = "REGRESSION CONFIRMED"
    else:
        verification_status = "INCONCLUSIVE"

    print(f"\nVerification status: {verification_status}")

    # 6. Final investigation summary
    print("\n" + "=" * 60)
    print("INVESTIGATION COMPLETE")
    print("=" * 60)

    print(f"Regression reproduced: YES")
    print(f"Failing repository: {target_repo}")
    print(f"Candidate commit: {commit_hash}")
    print(f"Counterfactual verification: {verification_status}")

    print("\nCausalTrace investigation finished.")


if __name__ == "__main__":
    main()

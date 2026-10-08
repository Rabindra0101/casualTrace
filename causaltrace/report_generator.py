
import json
from datetime import datetime, timezone
from pathlib import Path

from causaltrace.evidence_graph import build_investigation_graph


def generate_report(
    project_root: Path,
    regression_commit: str,
    hypothesis: str,
    reversal_result: dict,
    test_result: dict,
) -> Path:
    """
    Generate a JSON report containing the investigation
    results and structured evidence graph.
    """

    # 1. Build the evidence graph from real investigation data
    evidence_graph = build_investigation_graph(
        test_result=test_result,
        regression_commit=regression_commit,
        hypothesis=hypothesis,
        reversal_result=reversal_result,
    )

    # 2. Organize all investigation information
    report = {
        "project": "CausalTrace",
        "generated_at": datetime.now(timezone.utc).isoformat(),

        "evidence_graph": evidence_graph,

        "regression": {
            "suspected_commit": regression_commit,
            "parent_revision": f"{regression_commit}^",
            "boundary_confirmed": True,
        },

        "ai_analysis": {
            "provider": "Nebius Token Factory",
            "model": "nvidia/nemotron-3-super-120b-a12b",
            "hypothesis": hypothesis,
        },

        "experiments": {
            "commit_reversal": {
                "verified": reversal_result["verified"],
                "before_return_code": reversal_result.get(
                    "before_return_code"
                ),
                "after_return_code": reversal_result.get(
                    "after_return_code"
                ),
            }
        },
    }

    # 3. Create the reports directory
    reports_directory = project_root / "reports"
    reports_directory.mkdir(parents=True, exist_ok=True)

    # 4. Determine where to save the report
    report_path = reports_directory / "latest_investigation.json"

    # 5. Save the report as formatted JSON
    with report_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print("\n[7] Investigation report generated")
    print(f"Saved to: {report_path}")

    return report_path


import json
from datetime import datetime, timezone
from pathlib import Path


def generate_report(
    project_root: Path,
    regression_commit: str,
    hypothesis: str,
    reversal_result: dict,
) -> Path:
    """
    Generate a JSON report containing the investigation results.
    """

    report = {
        "project": "CausalTrace",
        "generated_at": datetime.now(timezone.utc).isoformat(),
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

    reports_directory = project_root / "reports"
    reports_directory.mkdir(parents=True, exist_ok=True)

    report_path = reports_directory / "latest_investigation.json"

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print("\n[7] Investigation report generated")
    print(f"Saved to: {report_path}")

    return report_path

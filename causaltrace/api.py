
import json
import subprocess
import sys
import threading
from pathlib import Path

from fastapi import FastAPI, HTTPException


app = FastAPI(
    title="CausalTrace API",
    description="Evidence-driven software regression investigation API",
    version="0.2.0",
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = PROJECT_ROOT / "reports" / "latest_investigation.json"

# Prevent two investigations from running simultaneously.
investigation_lock = threading.Lock()


@app.get("/")
def home():
    return {
        "application": "CausalTrace",
        "status": "running",
    }


@app.get("/api/investigation")
def get_investigation():
    """
    Return the latest saved investigation report.
    """
    if not REPORT_PATH.is_file():
        raise HTTPException(
            status_code=404,
            detail="No investigation report found. Run CausalTrace first.",
        )

    try:
        with REPORT_PATH.open("r", encoding="utf-8") as file:
            report = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        raise HTTPException(
            status_code=500,
            detail="Unable to read the investigation report.",
        ) from error

    return report


@app.get("/api/graph")
def get_evidence_graph():
    """
    Return the Evidence Graph from the latest report.
    """
    report = get_investigation()

    if "evidence_graph" not in report:
        raise HTTPException(
            status_code=404,
            detail="Evidence Graph is missing from the report.",
        )

    return report["evidence_graph"]


@app.post("/api/run-investigation")
def run_investigation():
    """
    Run the bundled demo investigation.

    The API does not accept arbitrary repository paths
    or shell commands.
    """
    if not investigation_lock.acquire(blocking=False):
        raise HTTPException(
            status_code=409,
            detail="An investigation is already running.",
        )

    try:
        result = subprocess.run(
            [sys.executable, "-X", "utf8", "-m", "causaltrace.main"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
            check=False,
        )

        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "Investigation process failed.",
                    "return_code": result.returncode,
                    "output": (result.stdout + "\n" + result.stderr)[-4000:],
                },
            )

        if not REPORT_PATH.is_file():
            raise HTTPException(
                status_code=500,
                detail="Investigation finished without generating a report.",
            )

        return {
            "status": "completed",
            "message": "Investigation process finished.",
            "return_code": result.returncode,
        }

    except subprocess.TimeoutExpired as error:
        raise HTTPException(
            status_code=504,
            detail="Investigation exceeded the 180-second timeout.",
        ) from error

    except OSError as error:
        raise HTTPException(
            status_code=500,
            detail="Unable to start the investigation process.",
        ) from error

    finally:
        investigation_lock.release()

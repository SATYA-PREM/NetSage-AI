from fastapi import APIRouter, HTTPException
from pathlib import Path
import csv

router = APIRouter()

DATA_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "cases.csv"
)


@router.get("")
def get_cases():

    if not DATA_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Cases file not found: {DATA_FILE}"
        )

    cases = []

    try:
        with open(
            DATA_FILE,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                case_id = (
                    row.get("case_id")
                    or row.get("id")
                    or ""
                ).strip()

                title = (
                    row.get("title")
                    or ""
                ).strip()

                # Support both versions of your CSV
                symptom = (
                    row.get("symptom")
                    or row.get("issue")
                    or row.get("description")
                    or ""
                ).strip()

                topology_note = (
                    row.get("topology_note")
                    or ""
                ).strip()

                show_outputs = (
                    row.get("show_outputs")
                    or ""
                ).strip()

                expected_fault = (
                    row.get("expected_fault")
                    or row.get("expected_root_cause")
                    or ""
                ).strip()

                osi_layer = (
                    row.get("osi_layer")
                    or ""
                ).strip()

                concept = (
                    row.get("concept")
                    or row.get("category")
                    or ""
                ).strip()

                severity = (
                    row.get("severity")
                    or "Medium"
                ).strip()

                if not case_id:
                    continue

                cases.append({
                    "case_id": case_id,
                    "title": title,

                    "symptom": symptom,
                    "topology_note": topology_note,
                    "show_outputs": show_outputs,

                    "expected_fault": expected_fault,
                    "osi_layer": osi_layer,
                    "concept": concept,
                    "severity": severity,

                    # Optional metadata
                    "device": row.get("device", ""),
                    "device_type": row.get("device_type", ""),
                    "status": row.get("status", "Open"),
                    "source_ip": row.get("source_ip", ""),
                    "destination_ip": row.get("destination_ip", ""),
                    "vlan_id": row.get("vlan_id", ""),
                    "interface": row.get("interface", ""),
                    "protocol": row.get("protocol", "")
                })

        return {
            "cases": cases,
            "count": len(cases)
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to read cases: {str(exc)}"
        )
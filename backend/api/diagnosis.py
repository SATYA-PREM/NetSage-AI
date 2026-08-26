import logging

from fastapi import APIRouter, HTTPException
from backend.models.diagnosis import (
    DiagnosisRequest,
    DiagnosisResponse
)
from backend.services.diagnosis_service import (
    diagnose_network_issue
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("")
async def create_diagnosis(
    request: DiagnosisRequest
) -> DiagnosisResponse:

    if not request.symptom.strip():

        raise HTTPException(
            status_code=400,
            detail="Symptom is required."
        )

    logger.info(
        "Diagnosis request received: case_id=%s device=%s",
        request.case_id or "CUSTOM",
        request.device or "unspecified"
    )

    return await diagnose_network_issue(
        case_id=request.case_id or "CUSTOM",
        symptom=request.symptom,
        topology=request.topology,
        command_output=request.command_output,
        device=request.device,
        device_type=request.device_type,
        severity=request.severity
    )
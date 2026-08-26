from typing import Any

from pydantic import BaseModel, Field


class DiagnosisRequest(BaseModel):

    case_id: str | None = Field(
        default="CUSTOM",
        description="Historical case ID, or CUSTOM for a new incident."
    )

    symptom: str = Field(
        min_length=1,
        description="Observed network problem."
    )

    topology: str = Field(
        default="",
        description="Packet Tracer topology or network context."
    )

    command_output: str = Field(
        default="",
        description="Raw Cisco show-command output."
    )

    device: str = ""
    device_type: str = ""
    severity: str = "Medium"


class GeminiEvidencePackage(BaseModel):

    incident: dict[str, Any] = Field(
        description="The submitted symptom, topology, command output, and device context."
    )
    deterministic_analysis: dict[str, Any] = Field(
        description="Focused deterministic analysis."
    )
    rule_engine_findings: list[dict[str, Any]] = Field(
        description="Rule checker findings provided to Gemini before synthesis."
    )
    similar_historical_cases: list[dict[str, Any]] = Field(
        description="Matched historical cases used as reference only."
    )
    matched_test_cases: list[dict[str, Any]] = Field(
        description="Historical test cases matched to the submitted symptom."
    )


class GeminiDiagnosisOutput(BaseModel):

    ai_available: bool = True
    category: str
    root_cause: str
    confidence: float = Field(ge=0.0, le=1.0)
    osi_layer: str
    evidence: list[str]
    recommended_commands: list[str]
    proposed_remediation: list[str]
    historical_case_analysis: list[str]
    uncertainties: list[str]
    human_review_required: bool = True


class DiagnosisResponse(BaseModel):

    diagnosis_id: str
    case_id: str
    status: str
    processing_status: str
    category: str

    root_cause: str = Field(
        description="Most likely root cause based only on supplied evidence."
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence from 0 to 1."
    )

    osi_layer: str | None = Field(
        description="Likely OSI layer involved."
    )

    evidence: list[str] = Field(
        default_factory=list,
        description="Specific evidence supporting the diagnosis."
    )

    recommended_commands: list[str] = Field(
        default_factory=list,
        description="Cisco commands needed to obtain more evidence."
    )

    proposed_remediation: list[str] = Field(
        default_factory=list,
        description="Proposed remediation steps."
    )

    more_evidence_required: bool = Field(
        description="Whether more evidence is required."
    )

    confidence_percent: int
    deterministic_findings: list[dict[str, Any]]
    similar_cases: list[dict[str, Any]]
    historical_case_analysis: list[str]
    uncertainties: list[str]
    ai_analysis: GeminiDiagnosisOutput
    gemini_input: GeminiEvidencePackage
    human_review_required: bool = True
    created_at: str
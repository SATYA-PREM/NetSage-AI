from pydantic import BaseModel


class Case(BaseModel):
    case_id: str
    title: str

    symptom: str
    topology_note: str = ""
    show_outputs: str = ""

    expected_fault: str = ""
    osi_layer: str = ""
    concept: str = ""
    severity: str = "Medium"


class CaseCreate(BaseModel):
    title: str

    symptom: str
    topology_note: str = ""
    show_outputs: str = ""

    expected_fault: str = ""
    osi_layer: str = ""
    concept: str = ""
    severity: str = "Medium"
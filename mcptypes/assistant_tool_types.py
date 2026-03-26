from pydantic import BaseModel, Field
from typing import Any, List, Optional
from mcptypes.error_type import StructuredError


class ColumnInfoVO(BaseModel):
    name: Optional[str] = ""
    type: Optional[str] = ""
    mode: Optional[str] = ""
    fieldDataType: Optional[str] = ""
    fieldOrder: Optional[int] = 0
    
    model_config = {
        "extra": "ignore"
    }


class RuleVO(BaseModel):
    ruleId: Optional[str] = ""
    ruleName: Optional[str] = ""
    ruleDescription: Optional[str] = ""
    model_config = {
        "extra": "ignore"
    }

class EvidenceVO(BaseModel):
    id: Optional[str] = ""
    name: Optional[str] = ""
    description: Optional[str] = ""
    fileName: Optional[str] = ""
    columnsInfo: Optional[List[ColumnInfoVO]] = None
    
    model_config = {
        "extra": "ignore"
    }


class LineageVO(BaseModel):
    originType: Optional[str] = ""
    recursionLevel: Optional[int] = 0
    linkedFrom: Optional[List['LinkedControlVO']] = None
    model_config = {
        "extra": "ignore"
    }

class LinkedControlVO(BaseModel):
    assessmentId: Optional[str] = ""
    assessmentName: Optional[str] = ""
    controlId: Optional[str] = ""
    controlName: Optional[str] = ""
    controlDescription: Optional[str] = ""
    referenceType: Optional[str] = ""
    lineage: Optional[List[LineageVO]] = None
    evidences: Optional[List[EvidenceVO]] = None
    rule: Optional[RuleVO] = None
    model_config = {
        "extra": "ignore"
    }


# Update forward reference after LinkedControlVO is defined
LineageVO.model_rebuild()


class ControlSourceSummaryVO(BaseModel):
    assessmentId: Optional[str] = ""
    assessmentName: Optional[str] = ""
    controlId: Optional[str] = ""
    controlName: Optional[str] = ""
    lineage: Optional[List[LineageVO]] = None
    model_config = {
        "extra": "ignore"
    }


class ControlSourceSummaryResponseVO(BaseModel):
    success: bool = True
    data: Optional[ControlSourceSummaryVO] = None
    error: Optional[StructuredError] = None
    next_action: Optional[str] = None
    next_step: Optional[str] = None
    model_config = {
        "extra": "ignore"
    }


class AssessmentCreateResponseVO(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    url: Optional[str] = None
    categoryName: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class ControlCitationSuggestionVO(BaseModel):
    Name: Optional[str] = ""
    control_id: Optional[str] = Field(default="", validation_alias="Control ID")
    control_classification: Optional[str] = Field(default="", validation_alias="Control Classification")
    impact_zone: Optional[str] = Field(default="", validation_alias="Impact Zone")
    control_requirement: Optional[str] = Field(default="", validation_alias="Control Requirement")
    sort_id: Optional[str] = Field(default="", validation_alias="Sort ID")
    control_type: Optional[str] = Field(default="", validation_alias="Control Type")
    score: Optional[float] = Field(default=0.0, validation_alias="Score")

    model_config = {
        "extra": "ignore",
        "populate_by_name": True
    }


class ControlCitationSuggestionItemVO(BaseModel):
    inputControlName: Optional[str] = ""
    controlId: Optional[str] = ""
    suggestions: Optional[List[ControlCitationSuggestionVO]] = None

    model_config = {
        "extra": "ignore"
    }


class ControlCitationSuggestionResponseVO(BaseModel):
    success: bool = True
    items: Optional[List[ControlCitationSuggestionItemVO]] = None
    authorityDocument: Optional[str] = ""
    next_action: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class AssessmentControlConfigVO(BaseModel):
    id: Optional[str] = ""
    name: Optional[str] = ""
    description: Optional[str] = ""
    alias: Optional[str] = ""
    controlNumber: Optional[str] = ""
    context: Optional[Any] = None
    additionalContext: Optional[Any] = None

    model_config = {
        "extra": "ignore"
    }


class AssessmentControlConfigListResponseVO(BaseModel):
    success: bool = True
    controls: Optional[List[AssessmentControlConfigVO]] = None
    totalCount: Optional[int] = 0
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class AssessmentListItemVO(BaseModel):
    id: Optional[str] = ""
    name: Optional[str] = ""
    categoryName: Optional[str] = ""

    model_config = {
        "extra": "ignore"
    }


class AssessmentListResponseVO(BaseModel):
    success: bool = True
    assessments: Optional[List[AssessmentListItemVO]] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class ControlConfigCreateVO(BaseModel):
    id: Optional[str] = ""
    displayable: Optional[str] = ""
    alias: Optional[str] = ""

    model_config = {
        "extra": "ignore"
    }


class ControlConfigCreateResponseVO(BaseModel):
    success: bool = True
    control: Optional[ControlConfigCreateVO] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class CitationDetailsVO(BaseModel):
    authorityDocument: Optional[str] = ""
    controlIdsInAuthorityDocument: Optional[List[str]] = None
    sortId: Optional[str] = ""
    controlNames: Optional[List[str]] = None

    model_config = {
        "extra": "ignore"
    }


class CitationAttachmentVO(BaseModel):
    id: Optional[str] = ""
    planControlID: Optional[str] = ""
    authorityDocument: Optional[str] = ""
    controlNames: Optional[List[str]] = None
    controlsInAuthorityDocument: Optional[List[str]] = None
    sortID: Optional[str] = ""
    status: Optional[str] = ""

    model_config = {
        "extra": "ignore"
    }


class CitationAttachmentResponseVO(BaseModel):
    success: bool = True
    message: Optional[str] = None
    assessmentId: Optional[str] = None
    controlId: Optional[str] = None
    citationDetails: Optional[CitationDetailsVO] = None
    next_step: Optional[str] = None
    next_action: Optional[str] = None
    citations: Optional[List[CitationAttachmentVO]] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class SqlQueryEvidenceMutationResponseVO(BaseModel):
    success: bool = True
    message: Optional[str] = None
    controlConfigId: Optional[str] = None
    evidenceId: Optional[str] = None
    sqlQuery: Optional[str] = None
    newEvidenceName: Optional[str] = None
    referedEvidenceNames: Optional[List[str]] = None
    next_step: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class SqlQueryEvidenceItemVO(BaseModel):
    evidenceId: Optional[str] = ""
    sqlQuery: Optional[str] = ""
    evidenceName: Optional[str] = ""
    referedEvidenceNames: Optional[List[str]] = None

    model_config = {
        "extra": "ignore"
    }


class SqlQueryEvidenceListResponseVO(BaseModel):
    success: bool = True
    evidences: Optional[List[SqlQueryEvidenceItemVO]] = None
    totalCount: Optional[int] = 0
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class EvidenceSampleResponseVO(BaseModel):
    success: bool = True
    controlId: Optional[str] = None
    evidences: Optional[List[Any]] = None
    next_action: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class EntityHierarchyResponseVO(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class ContextTableVO(BaseModel):
    headerRow: Optional[List[str]] = None
    dataRows: Optional[List[List[str]]] = None

    model_config = {
        "extra": "ignore"
    }


class ContextTablesResponseVO(BaseModel):
    success: bool = True
    entity_hierarchy: Optional[ContextTableVO] = None
    control_additional_context: Optional[ContextTableVO] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class NoteMutationResponseVO(BaseModel):
    success: bool = True
    message: Optional[str] = None
    controlConfigId: Optional[str] = None
    noteId: Optional[str] = None
    topic: Optional[str] = None
    notes: Optional[str] = None
    next_step: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class NoteItemVO(BaseModel):
    id: Optional[str] = ""
    topic: Optional[str] = ""
    notes: Optional[str] = ""

    model_config = {
        "extra": "ignore"
    }


class NoteListResponseVO(BaseModel):
    success: bool = True
    notes: Optional[List[NoteItemVO]] = None
    totalCount: Optional[int] = 0
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class SqlValidationResponseVO(BaseModel):
    success: bool = True
    resp: Optional[Any] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class ReadyForExecutionResponseVO(BaseModel):
    success: bool = True
    message: Optional[str] = None
    response: Optional[Any] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class CustomControlConfigDataVO(BaseModel):
    assessment_id: Optional[str] = None

    model_config = {
        "extra": "ignore"
    }


class CustomControlConfigResponseVO(BaseModel):
    success: bool = True
    data: Optional[CustomControlConfigDataVO] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class UpdateControlContextsResponseVO(BaseModel):
    success: bool = True
    controlConfigId: Optional[str] = None
    message: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }

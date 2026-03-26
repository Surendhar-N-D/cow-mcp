from pydantic import BaseModel, Field
from typing import List, Optional, Any
from mcptypes.assets_tools_type import AssetVO
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
    assessmentMetricsId: Optional[str] = Field("", validation_alias="assessmentId")
    assessmentMetricsName: Optional[str] = Field("", validation_alias="assessmentName")
    metricsId: Optional[str] = Field("", validation_alias="controlId")
    metricsName: Optional[str] = Field("", validation_alias="controlName")
    metricsDescription: Optional[str] = Field("", validation_alias="controlDescription")
    referenceType: Optional[str] = ""

    lineage: Optional[List[LineageVO]] = None
    evidences: Optional[List[EvidenceVO]] = None
    rule: Optional[RuleVO] = None

    model_config = {
        "extra": "ignore",
        "populate_by_name": True
    }


# Update forward reference after LinkedControlVO is defined
LineageVO.model_rebuild()


class MetricsSourceSummaryVO(BaseModel):
    assessmentMetricsId: Optional[str] = Field("", validation_alias="assessmentId")
    assessmentMetricsName: Optional[str] = Field("", validation_alias="assessmentName")
    metricsId: Optional[str] = Field("", validation_alias="controlId")
    metricsName: Optional[str] = Field("", validation_alias="controlName")

    lineage: Optional[List[LineageVO]] = None

    model_config = {
        "extra": "ignore",
        "populate_by_name": True
    }

class MetricsSourceSummaryResponseVO(BaseModel):
    success: bool = True
    data: Optional[MetricsSourceSummaryVO] = None
    error: Optional[StructuredError] = None
    next_action: Optional[str] = None
    next_step: Optional[str] = None
    model_config = {
        "extra": "ignore"
    }


class MetricsAssessmentResponseVO(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class MetricsAssetListResponseVO(BaseModel):
    success: bool = True
    data: Optional[List[AssetVO]] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class AssetDataEvidenceVO(BaseModel):
    evidenceName: Optional[str] = ""
    evidenceDescription: Optional[str] = ""

    model_config = {
        "extra": "ignore"
    }


class AssetMetricVO(BaseModel):
    metricsId: Optional[str] = ""
    metricsName: Optional[str] = ""
    metricsDescription: Optional[str] = ""
    evidence: Optional[List[AssetDataEvidenceVO]] = None

    model_config = {
        "extra": "ignore"
    }


class AssetDataVO(BaseModel):
    assetName: Optional[str] = ""
    assetId: Optional[str] = ""
    requiresNarrowing: Optional[bool] = False
    metrics: Optional[List[AssetMetricVO]] = None

    model_config = {
        "extra": "ignore"
    }


class AssetDataResponseVO(BaseModel):
    success: bool = True
    data: Optional[AssetDataVO] = None
    next_action: Optional[str] = None
    next_step: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class AssetMetricEvidenceSampleVO(BaseModel):
    evidenceRunId: Optional[str] = ""
    evidenceName: Optional[str] = ""
    evidenceDescription: Optional[str] = ""
    sampleRecords: Optional[List[dict]] = None
    error: Optional[str] = ""

    model_config = {
        "extra": "ignore"
    }


class AssetMetricEvidenceDataVO(BaseModel):
    metricsId: Optional[str] = ""
    metricsName: Optional[str] = ""
    metricsDescription: Optional[str] = ""
    evidence: Optional[List[AssetMetricEvidenceSampleVO]] = None

    model_config = {
        "extra": "ignore"
    }


class AssetMetricsEvidenceSampleDataVO(BaseModel):
    assetId: Optional[str] = ""
    metrics: Optional[List[AssetMetricEvidenceDataVO]] = None

    model_config = {
        "extra": "ignore"
    }


class AssetMetricsEvidenceSampleResponseVO(BaseModel):
    success: bool = True
    data: Optional[AssetMetricsEvidenceSampleDataVO] = None
    errors: Optional[List[Any]] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class MetricsRunDataVO(BaseModel):
    runId: Optional[str] = ""
    status: Optional[str] = ""
    name: Optional[str] = ""
    description: Optional[str] = ""

    model_config = {
        "extra": "ignore"
    }


class MetricsRunResponseVO(BaseModel):
    success: bool = True
    data: Optional[MetricsRunDataVO] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class RecentMetricsRunItemVO(BaseModel):
    metricAssessmentRunId: Optional[str] = ""
    name: Optional[str] = ""
    runTime: Optional[str] = ""
    status: Optional[str] = ""

    model_config = {
        "extra": "ignore"
    }


class RecentMetricsRunListResponseVO(BaseModel):
    success: bool = True
    data: Optional[List[RecentMetricsRunItemVO]] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class MetricEvidenceFormulaVO(BaseModel):
    filteringExpression: Optional[str] = ""
    compliantExpression: Optional[str] = ""

    model_config = {
        "extra": "ignore"
    }


class MetricEvidenceItemVO(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    metricScore: Optional[Any] = None
    cel_formula: Optional[MetricEvidenceFormulaVO] = None
    message: Optional[str] = None

    model_config = {
        "extra": "ignore"
    }


class MetricEvidenceSourceVO(BaseModel):
    name: Optional[str] = ""
    status: Optional[str] = ""

    model_config = {
        "extra": "ignore"
    }


class MetricRunItemVO(BaseModel):
    metricRunId: Optional[str] = ""
    name: Optional[str] = ""
    description: Optional[str] = ""
    metricId: Optional[str] = ""
    metricNumber: Optional[str] = ""
    formula: Optional[str] = ""
    metricEvidences: Optional[List[MetricEvidenceItemVO]] = None
    metricEvidencesSources: Optional[List[MetricEvidenceSourceVO]] = None

    model_config = {
        "extra": "ignore"
    }


class MetricsRunDetailsDataVO(BaseModel):
    assessmentMetricsRunId: Optional[str] = ""
    assessmentMetricsId: Optional[str] = ""
    metrics: Optional[List[MetricRunItemVO]] = None

    model_config = {
        "extra": "ignore"
    }


class MetricsRunDetailsResponseVO(BaseModel):
    success: bool = True
    data: Optional[MetricsRunDetailsDataVO] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class MetricCreateDataVO(BaseModel):
    metricsId: Optional[str] = ""

    model_config = {
        "extra": "ignore"
    }


class MetricCreateResponseVO(BaseModel):
    success: bool = True
    data: Optional[MetricCreateDataVO] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class MetricUpdateResponseVO(BaseModel):
    success: bool = True
    message: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class MetricsCategoryListResponseVO(BaseModel):
    success: bool = True
    data: Optional[List[str]] = None
    message: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class AssessmentMetricItemVO(BaseModel):
    id: Optional[str] = ""
    name: Optional[str] = ""
    description: Optional[str] = ""
    alias: Optional[str] = ""
    metricNumber: Optional[str] = ""

    model_config = {
        "extra": "ignore"
    }


class AssessmentMetricsListResponseVO(BaseModel):
    success: bool = True
    metrics: Optional[List[AssessmentMetricItemVO]] = None
    totalCount: Optional[int] = 0
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class MetricCitationSuggestionVO(BaseModel):
    Name: Optional[str] = ""
    metric_id: Optional[str] = Field(default="", validation_alias="Metric ID")
    metric_classification: Optional[str] = Field(default="", validation_alias="Metric Classification")
    impact_zone: Optional[str] = Field(default="", validation_alias="Impact Zone")
    metric_requirement: Optional[str] = Field(default="", validation_alias="Metric Requirement")
    sort_id: Optional[str] = Field(default="", validation_alias="Sort ID")
    metric_type: Optional[str] = Field(default="", validation_alias="Metric Type")
    score: Optional[float] = Field(default=0.0, validation_alias="Score")

    model_config = {
        "extra": "ignore",
        "populate_by_name": True
    }


class MetricCitationSuggestionItemVO(BaseModel):
    inputMetricName: Optional[str] = ""
    metricsId: Optional[str] = ""
    suggestions: Optional[List[MetricCitationSuggestionVO]] = None

    model_config = {
        "extra": "ignore"
    }


class MetricCitationSuggestionResponseVO(BaseModel):
    success: bool = True
    items: Optional[List[MetricCitationSuggestionItemVO]] = None
    authorityDocument: Optional[str] = ""
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class MetricCitationAttachmentVO(BaseModel):
    id: Optional[str] = ""
    metricsID: Optional[str] = ""
    authorityDocument: Optional[str] = ""
    metricsNames: Optional[List[str]] = None
    metricsIdsInAuthorityDocument: Optional[List[str]] = None
    sortID: Optional[str] = ""
    status: Optional[str] = ""

    model_config = {
        "extra": "ignore"
    }


class MetricCitationAttachmentResponseVO(BaseModel):
    success: bool = True
    citations: Optional[List[MetricCitationAttachmentVO]] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class MetricsEvidenceSampleResponseVO(BaseModel):
    success: bool = True
    metricsRunId: Optional[str] = None
    evidences: Optional[List[Any]] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class MetricsSqlValidationResponseVO(BaseModel):
    success: bool = True
    resp: Optional[Any] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class MetricSqlQueryEvidenceMutationResponseVO(BaseModel):
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


class MetricSqlQueryEvidenceItemVO(BaseModel):
    evidenceId: Optional[str] = ""
    sqlQuery: Optional[str] = ""
    evidenceName: Optional[str] = ""
    referedEvidenceNames: Optional[List[str]] = None

    model_config = {
        "extra": "ignore"
    }


class MetricSqlQueryEvidenceListResponseVO(BaseModel):
    success: bool = True
    evidences: Optional[List[MetricSqlQueryEvidenceItemVO]] = None
    totalCount: Optional[int] = 0
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class CelMutationResponseVO(BaseModel):
    success: bool = True
    message: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class CelExpressionResponseVO(BaseModel):
    success: bool = True
    filteringExpression: Optional[str] = None
    compliantExpression: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class MetricNoteMutationResponseVO(BaseModel):
    success: bool = True
    message: Optional[str] = None
    metricsId: Optional[str] = None
    noteId: Optional[str] = None
    topic: Optional[str] = None
    notes: Optional[str] = None
    next_step: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class MetricNoteItemVO(BaseModel):
    id: Optional[str] = ""
    topic: Optional[str] = ""
    notes: Optional[str] = ""

    model_config = {
        "extra": "ignore"
    }


class MetricNoteListResponseVO(BaseModel):
    success: bool = True
    notes: Optional[List[MetricNoteItemVO]] = None
    totalCount: Optional[int] = 0
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class LinkMetricsResponseVO(BaseModel):
    success: bool = True
    message: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }

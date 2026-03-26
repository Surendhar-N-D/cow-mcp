from dataclasses import MISSING, asdict, dataclass, fields, is_dataclass
from datetime import datetime
from typing import Any, Dict, List, get_type_hints,Optional
from pydantic import BaseModel
from mcptypes.assets_tools_type import AssetVO
from mcptypes.error_type import StructuredError


def _to_dict(obj: Any) -> Any:
    """Recursively turn dataclasses/lists/primitives into plain dicts/lists."""
    if is_dataclass(obj):
        return {k: _to_dict(v) for k, v in asdict(obj).items()}
    if isinstance(obj, list):
        return [_to_dict(item) for item in obj]
    if isinstance(obj, dict):
        return {k: _to_dict(v) for k, v in obj.items()}
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj


def _from_dict(cls: type, data: Any) -> Any:
    """Recursively reconstruct dataclasses from plain dicts/lists."""
    if data is None:
        return data
    if cls == datetime:
        return datetime.fromisoformat(data)
    if getattr(cls, "__origin__", None) == list:
        element_type = cls.__args__[0]
        return [_from_dict(element_type, item) for item in data]
    if getattr(cls, "__origin__", None) == dict:
        return data  # dict[str, Any] -> already plain dict
    if is_dataclass(cls):
        kwargs = {}
        type_hints = get_type_hints(cls)
        for f in fields(cls):
            # Handle missing fields properly
            if f.name in data:
                value = data[f.name]
            elif f.default is not MISSING:
                # Use the default value if field is missing
                value = f.default
            elif f.default_factory is not MISSING:
                # Use the default factory if available
                value = f.default_factory()
            else:
                # Set sensible defaults for required fields that are missing
                field_type = type_hints.get(f.name, str)
                if field_type == bool:
                    value = False
                elif field_type == int:
                    value = 0
                elif field_type == str:
                    value = ""
                elif field_type == list or getattr(field_type, "__origin__", None) == list:
                    value = []
                elif field_type == dict or getattr(field_type, "__origin__", None) == dict:
                    value = {}
                else:
                    value = None

            kwargs[f.name] = _from_dict(type_hints.get(f.name, type(value)), value)
        return cls(**kwargs)
    # primitive type
    return data


@dataclass
class TaskInputVO:
    name: str
    description: str
    dataType: str
    defaultValue: str
    showField: bool
    required: bool
    allowUserValues: bool = True
    allowedValues: List[Any] = None
    templateFile: str = ""
    format: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return _to_dict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskInputVO":
        return _from_dict(cls, data)


@dataclass
class TaskOutputVO:
    name: str
    description: str
    dataType: str

    def to_dict(self) -> Dict[str, Any]:
        return _to_dict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskOutputVO":
        return _from_dict(cls, data)


@dataclass
class TaskVO:
    name: str
    displayName: str
    version: str
    description: str
    type: str
    tags: List[str]
    applicationType: str
    inputs: List[TaskInputVO]
    outputs: List[TaskOutputVO]
    appTags: Dict[str, List[str]]
    readmeData: str

    def to_dict(self) -> Dict[str, Any]:
        return _to_dict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskVO":
        return _from_dict(cls, data)

        
class SimplifiedRuleVO(BaseModel):
    id: Optional[str] = ""
    
    name: Optional[str] = ""
    purpose: Optional[str] = ""
    description: Optional[str] = ""

    model_config = {
        "extra": "ignore"
    }

class SimplifiedRulesAndTasksSuggestionVO(BaseModel):
    name: Optional[str] = ""
    purpose: Optional[str] = ""
    description: Optional[str] = ""

    model_config = {
        "extra": "ignore"
    }

class SimplifiedRuleListVO(BaseModel):
    success: bool = True
    rules: Optional[List[SimplifiedRuleVO]] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}

class AssessmentVO(BaseModel):
    id: Optional[str] = ""
    name: Optional[str] = ""
    categoryName: Optional[str] = ""

    model_config = {
        "extra": "ignore"
    }

class AssessmentListVO(BaseModel):
    success: bool = True
    assessments: Optional[List[AssessmentVO]] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}

class AssessmentControlVO(BaseModel):
    id: Optional[str] = ""
    name: Optional[str] = ""
    alias: Optional[str] = ""
    ruleId: Optional[str] = ""

    model_config = {
        "extra": "ignore"
    }


class AssessmentControlListResponseVO(BaseModel):
    success: bool = True
    controls: Optional[List[AssessmentControlVO]] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class VerifyControlInAssessmentResponseVO(BaseModel):
    success: bool = True
    assessment_name: Optional[str] = None
    control_alias: Optional[str] = None
    control_info: Optional[Any] = None
    warning: Optional[str] = None
    message: Optional[str] = None
    next_actions: Optional[List[str]] = None
    ready_for_attachment: Optional[bool] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class ApplicationsPublishStatusResponseVO(BaseModel):
    success: bool = True
    app_info: Optional[List[Any]] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class RulePublishStatusResponseVO(BaseModel):
    success: bool = True
    published: bool = False
    rule_info: Optional[List[Any]] = None
    message: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class PublishApplicationResponseVO(BaseModel):
    success: bool = True
    published: bool = False
    successful_apps: Optional[List[Any]] = None
    failed_apps: Optional[List[Any]] = None
    message: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class ControlAutomationResponseVO(BaseModel):
    success: bool = True
    control_id: Optional[str] = None
    control_name: Optional[str] = None
    automated: bool = False
    rule_id: Optional[str] = None
    rule_info: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class TaskSuggestionResponseVO(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class SupportTicketResponseVO(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class ApplicationItemVO(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    appType: Optional[str] = None
    othersTags: Optional[Dict[str, Any]] = None

    model_config = {"extra": "ignore"}


class ApplicationsForTagResponseVO(BaseModel):
    success: bool = True
    tag_name: Optional[str] = None
    additional_tags: Optional[Dict[str, List[str]]] = None
    applications: Optional[List[ApplicationItemVO]] = None
    count: int = 0
    message: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class AttachRuleToControlResponseVO(BaseModel):
    success: bool = True
    rule_id: Optional[str] = None
    rule_name: Optional[str] = None
    assessment_name: Optional[str] = None
    control_id: Optional[str] = None
    attachment_status: Optional[str] = None
    evidence_created: Optional[bool] = None
    evidence_info: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class RuleFetchResponseVO(BaseModel):
    success: bool = True
    rule_id: Optional[str] = None
    rule_name: Optional[str] = None
    data: Optional[Any] = None
    next_actions: Optional[List[str]] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class PublishRuleResponseVO(BaseModel):
    success: bool = True
    published: bool = False
    cc_rule_id: Optional[str] = None
    rule_info: Optional[List[Any]] = None
    message: Optional[str] = None
    ui_display_message: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class TemplateGuidanceResponseVO(BaseModel):
    success: bool = True
    task_name: Optional[str] = None
    input_name: Optional[str] = None
    input_description: Optional[str] = None
    format: Optional[str] = None
    decoded_template: Optional[str] = None
    guidance: Optional[Any] = None
    example_content: Optional[str] = None
    validation_rules: Optional[Any] = None
    presentation_format: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class CollectTemplateInputResponseVO(BaseModel):
    success: bool = True
    task_name: Optional[str] = None
    input_name: Optional[str] = None
    validated_content: Optional[str] = None
    content_preview: Optional[str] = None
    needs_final_confirmation: Optional[bool] = None
    data_type: Optional[str] = None
    format: Optional[str] = None
    is_file_type: Optional[bool] = None
    final_confirmation_message: Optional[str] = None
    message: Optional[str] = None
    ready_for_rule_update: Optional[bool] = None
    validation_errors: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class ConfirmTemplateInputResponseVO(BaseModel):
    success: bool = True
    task_name: Optional[str] = None
    input_name: Optional[str] = None
    file_url: Optional[str] = None
    stored_content: Optional[str] = None
    filename: Optional[str] = None
    content_size: Optional[int] = None
    storage_type: Optional[str] = None
    data_type: Optional[str] = None
    format: Optional[str] = None
    timestamp: Optional[str] = None
    rule_name: Optional[str] = None
    rule_updated: Optional[bool] = None
    rule_status: Optional[str] = None
    rule_progress: Optional[int] = None
    message: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class UploadFileResponseVO(BaseModel):
    success: bool = True
    file_url: Optional[str] = None
    filename: Optional[str] = None
    unique_filename: Optional[str] = None
    file_id: Optional[str] = None
    file_format: Optional[str] = None
    content_size: Optional[int] = None
    validation_status: Optional[str] = None
    was_formatted: Optional[bool] = None
    message: Optional[str] = None
    supported_encodings: Optional[List[str]] = None
    suggestion: Optional[str] = None
    exception_type: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class CollectParameterInputResponseVO(BaseModel):
    success: bool = True
    task_name: Optional[str] = None
    input_name: Optional[str] = None
    needs_default_confirmation: Optional[bool] = None
    default_value: Optional[Any] = None
    data_type: Optional[str] = None
    required: Optional[bool] = None
    confirmation_message: Optional[str] = None
    validated_value: Optional[Any] = None
    needs_final_confirmation: Optional[bool] = None
    final_confirmation_message: Optional[str] = None
    needs_user_input: Optional[bool] = None
    presentation: Optional[str] = None
    has_default: Optional[bool] = None
    message: Optional[str] = None
    validation_errors: Optional[List[str]] = None
    expected_type: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class ConfirmParameterInputResponseVO(BaseModel):
    success: bool = True
    task_name: Optional[str] = None
    input_name: Optional[str] = None
    stored_value: Optional[Any] = None
    data_type: Optional[str] = None
    required: Optional[bool] = None
    storage_type: Optional[str] = None
    confirmation_type: Optional[str] = None
    timestamp: Optional[str] = None
    rule_name: Optional[str] = None
    rule_updated: Optional[bool] = None
    rule_status: Optional[str] = None
    rule_progress: Optional[int] = None
    message: Optional[str] = None
    validation_errors: Optional[List[str]] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class InputCollectionOverviewResponseVO(BaseModel):
    success: bool = True
    input_analysis: Optional[Any] = None
    overview_presentation: Optional[str] = None
    task_alias_map: Optional[Any] = None
    task_input_groups: Optional[Any] = None
    mandatory_collection_plan: Optional[Any] = None
    rule_creation_ready: Optional[bool] = None
    selected_tasks: Optional[List[Any]] = None
    initial_inputs: Optional[Any] = None
    initial_inputs_meta: Optional[List[Any]] = None
    validation_checkpoint_count: Optional[int] = None
    message: Optional[str] = None
    next_action: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class VerifyCollectedInputsResponseVO(BaseModel):
    success: bool = True
    verification_summary: Optional[Any] = None
    verification_presentation: Optional[str] = None
    ready_for_creation: Optional[bool] = None
    missing_count: Optional[int] = None
    structured_inputs: Optional[Any] = None
    inputs_meta: Optional[List[Any]] = None
    task_input_mapping: Optional[Any] = None
    task_alias_map: Optional[Any] = None
    rule_finalization_ready: Optional[bool] = None
    message: Optional[str] = None
    next_action: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class ExecuteTaskResponseVO(BaseModel):
    success: bool = True
    execution_status: Optional[str] = None
    task_name: Optional[str] = None
    task_inputs: Optional[Dict[str, Any]] = None
    outputs: Optional[Dict[str, Any]] = None
    output_files: Optional[Dict[str, Any]] = None
    errors: Optional[List[Any]] = None
    required_app_type: Optional[List[str]] = None
    input_name: Optional[str] = None
    missing_inputs: Optional[List[str]] = None
    hint: Optional[str] = None
    next_action: Optional[str] = None
    message: Optional[str] = None
    exception_type: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class ExecutionProgressResponseVO(BaseModel):
    success: bool = True
    continue_polling: Optional[bool] = None
    polling_interval_seconds: Optional[int] = None
    display_mode: Optional[str] = None
    status: Optional[str] = None
    rule_name: Optional[str] = None
    execution_id: Optional[str] = None
    overall_progress_percentage: Optional[int] = None
    task_stats: Optional[Dict[str, Any]] = None
    display_lines: Optional[List[Any]] = None
    display_header: Optional[str] = None
    display_footer: Optional[str] = None
    transaction_count: Optional[int] = None
    unique_task_count: Optional[int] = None
    timestamp: Optional[str] = None
    completion_summary: Optional[Dict[str, Any]] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class FetchOutputFileResponseVO(BaseModel):
    success: bool = True
    file_url: Optional[str] = None
    filename: Optional[str] = None
    file_format: Optional[str] = None
    file_size_kb: Optional[float] = None
    display_content: Optional[str] = None
    user_message: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class FetchApplicationsResponseVO(BaseModel):
    success: bool = True
    applications: Optional[List[Any]] = None
    message: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class PrepareApplicationsForExecutionResponseVO(BaseModel):
    success: bool = True
    rule_name: Optional[str] = None
    app_type_tasks: Optional[Dict[str, Any]] = None
    tasks_needing_apps: Optional[List[Any]] = None
    needs_differentiation: Optional[Dict[str, Any]] = None
    total_app_types: Optional[int] = None
    applications_required: Optional[bool] = None
    guidance: Optional[List[str]] = None
    next_steps: Optional[List[str]] = None
    message: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class CheckRuleStatusResponseVO(BaseModel):
    success: bool = True
    status_info: Optional[Dict[str, Any]] = None
    rule_structure_summary: Optional[Dict[str, Any]] = None
    auto_inference_details: Optional[Dict[str, Any]] = None
    suggested_action: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class DesignNotesPreviewResponseVO(BaseModel):
    success: bool = True
    rule_name: Optional[str] = None
    design_notes_structure: Optional[Dict[str, Any]] = None
    sections_count: Optional[int] = None
    message: Optional[str] = None
    next_action: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class DesignNotesMutationResponseVO(BaseModel):
    success: bool = True
    rule_name: Optional[str] = None
    filename: Optional[str] = None
    sections_saved: Optional[int] = None
    message: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class FetchRuleDesignNotesResponseVO(BaseModel):
    success: bool = True
    rule_name: Optional[str] = None
    filename: Optional[str] = None
    designNotesContent: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class RuleReadmePreviewResponseVO(BaseModel):
    success: bool = True
    rule_name: Optional[str] = None
    readme_content: Optional[str] = None
    sections_count: Optional[int] = None
    estimated_length: Optional[str] = None
    message: Optional[str] = None
    next_action: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class RuleReadmeMutationResponseVO(BaseModel):
    success: bool = True
    rule_name: Optional[str] = None
    filename: Optional[str] = None
    content_length: Optional[int] = None
    sections_saved: Optional[int] = None
    message: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class ApplicationInfoResponseVO(BaseModel):
    success: bool = True
    app_name: Optional[str] = None
    supportedCreds: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class AddUniqueIdentifierResponseVO(BaseModel):
    success: bool = True
    rule_name: Optional[str] = None
    task_alias: Optional[str] = None
    identifier_added: Optional[Dict[str, Any]] = None
    updated_app_tags: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    next_step: Optional[str] = None
    application_config_example: Optional[Dict[str, Any]] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class RulesSuggestionResponseVO(BaseModel):
    success: bool = True
    rules: Optional[List[SimplifiedRulesAndTasksSuggestionVO]] = None
    message: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class TaskInputDetailsVO(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    dataType: Optional[str] = None
    required: Optional[bool] = None
    has_template: Optional[bool] = None
    format: Optional[str] = None

    model_config = {"extra": "ignore"}


class TaskOutputDetailsVO(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    dataType: Optional[str] = None

    model_config = {"extra": "ignore"}


class TaskDetailsResponseVO(BaseModel):
    success: bool = True
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    appTags: Optional[Dict[str, List[str]]] = None
    readme_content: Optional[str] = None
    inputs: Optional[List[TaskInputDetailsVO]] = None
    outputs: Optional[List[TaskOutputDetailsVO]] = None
    template_count: Optional[int] = None
    message: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class ExecuteRuleResponseVO(BaseModel):
    success: bool = True
    rule_name: Optional[str] = None
    execution_id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class RuleOutputSchemaConfigResponseVO(BaseModel):
    success: bool = True
    user_prompt: Optional[str] = None
    message: Optional[str] = None
    next_step: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class RuleCreateUpdateResponseVO(BaseModel):
    success: bool = True
    rule_id: Optional[str] = None
    rule_name: Optional[str] = None
    is_update: Optional[bool] = None
    detected_status: Optional[str] = None
    creation_phase: Optional[str] = None
    progress_percentage: Optional[int] = None
    completion_analysis: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    rule_structure: Optional[Dict[str, Any]] = None
    yaml_preview: Optional[str] = None
    timestamp: Optional[str] = None
    status: Optional[str] = None
    design_notes_info: Optional[Dict[str, Any]] = None
    readme_info: Optional[Dict[str, Any]] = None
    tag_status: Optional[Dict[str, Any]] = None
    ui_url: Optional[str] = None
    next_step: Optional[str] = None
    validation_errors: Optional[List[Any]] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class RuleDetailsResponseVO(BaseModel):
    success: bool = True
    rule_name: Optional[str] = None
    rule_structure: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class AssetListResponseVO(BaseModel):
    success: bool = True
    assets: Optional[List[AssetVO]] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class CheckItemVO(BaseModel):
    id: Optional[str] = ""
    name: Optional[str] = ""
    controlId: Optional[str] = ""

    model_config = {"extra": "ignore"}


class CheckListResponseVO(BaseModel):
    success: bool = True
    checks: Optional[List[CheckItemVO]] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class ControlHierarchyItemVO(BaseModel):
    id: Optional[str] = ""
    name: Optional[str] = ""
    planControls: Optional[List["ControlHierarchyItemVO"]] = None

    model_config = {"extra": "ignore"}


ControlHierarchyItemVO.model_rebuild()


class AssetControlHierarchyResponseVO(BaseModel):
    success: bool = True
    planControls: Optional[List[ControlHierarchyItemVO]] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class AddCheckToAssetResponseVO(BaseModel):
    success: bool = True
    controlId: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class CreateAssetAndCheckDataVO(BaseModel):
    assetId: Optional[str] = None
    parentControlId: Optional[str] = None
    controlId: Optional[str] = None
    checkId: Optional[str] = None

    model_config = {"extra": "ignore"}


class CreateAssetAndCheckResponseVO(BaseModel):
    success: bool = True
    response: Optional[CreateAssetAndCheckDataVO] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class ScheduleAssetExecutionResponseVO(BaseModel):
    success: bool = True
    scheduleId: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class AssetScheduleItemVO(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    controlPeriod: Optional[Any] = None
    cronTab: Optional[str] = None
    status: Optional[str] = None

    model_config = {"extra": "ignore"}


class AssetScheduleListResponseVO(BaseModel):
    success: bool = True
    items: Optional[List[AssetScheduleItemVO]] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class DeleteAssetScheduleResponseVO(BaseModel):
    success: bool = True
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class ControlCitationSuggestionVO(BaseModel):
    Name: Optional[str] = ""
    control_id: Optional[str] = ""
    control_classification: Optional[str] = ""
    impact_zone: Optional[str] = ""
    control_requirement: Optional[str] = ""
    sort_id: Optional[str] = ""
    control_type: Optional[str] = ""
    score: Optional[float] = 0.0

    model_config = {"extra": "ignore"}


class ControlCitationSuggestionItemVO(BaseModel):
    inputControlName: Optional[str] = ""
    controlId: Optional[str] = ""
    suggestions: Optional[List[ControlCitationSuggestionVO]] = None

    model_config = {"extra": "ignore"}


class ControlCitationSuggestionResponseVO(BaseModel):
    success: bool = True
    items: Optional[List[ControlCitationSuggestionItemVO]] = None
    authorityDocument: Optional[str] = ""
    next_action: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class AddCitationToAssetControlResponseVO(BaseModel):
    success: bool = True
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class ControlNoteMutationResponseVO(BaseModel):
    success: bool = True
    message: Optional[str] = None
    controlId: Optional[str] = None
    noteId: Optional[str] = None
    topic: Optional[str] = None
    notes: Optional[str] = None
    next_step: Optional[str] = None
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}


class ControlNoteItemVO(BaseModel):
    id: Optional[str] = ""
    topic: Optional[str] = ""
    notes: Optional[str] = ""

    model_config = {"extra": "ignore"}


class ControlNoteListResponseVO(BaseModel):
    success: bool = True
    notes: Optional[List[ControlNoteItemVO]] = None
    totalCount: Optional[int] = 0
    error: Optional[StructuredError] = None

    model_config = {"extra": "ignore"}

from pydantic import BaseModel, Field
from typing import Any, List, Optional
from enum import Enum
from mcptypes.error_type import StructuredError


class WorkflowEventCategoryItemVO(BaseModel):
    type: Optional[str] = ""
    displayable: Optional[str] = ""
    model_config = {
        "extra": "ignore"
    }

class WorkflowEventCategoryListVO(BaseModel):
    eventCategories: Optional[List[WorkflowEventCategoryItemVO]] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class WorkflowActivityCategoryItemVO(BaseModel):
    displayable: Optional[str] = ""
    model_config = {
        "extra": "ignore"
    }

class WorkflowActivityCategoryListVO(BaseModel):
    activityCategories: Optional[List[WorkflowActivityCategoryItemVO]] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }

    
class WorkflowConditionCategoryItemVO(BaseModel):
    displayable: Optional[str] = ""
    model_config = {
        "extra": "ignore"
    }

class WorkflowConditionCategoryListVO(BaseModel):
    conditionCategories: Optional[List[WorkflowConditionCategoryItemVO]] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }

class WorkflowInputsVO(BaseModel):
    name: Optional[str] = ""
    desc: Optional[str] = ""
    type: Optional[str] = ""
    options: Optional[str] = ""
    optional: Optional[bool] = False
    resource: Optional[str] = ""
    model_config = {
        "extra": "ignore"
    }

class WorkflowOutputsVO(BaseModel):
    name: Optional[str] = ""
    desc: Optional[str] = ""
    type: Optional[str] = ""
    possible_values: Optional[List[str]] = None
    isPrimaryOutcome: Optional[bool] = False
    model_config = {
        "extra": "ignore"
    }

class WorkflowPayloadVO(BaseModel):
    name: Optional[str] = ""
    desc: Optional[str] = ""
    type: Optional[str] = ""
    possible_values: Optional[List[str]] = None
    model_config = {
        "extra": "ignore"
    }

class WorkflowEventVO(BaseModel):
    id: Optional[str] = ""
    categoryId: Optional[str] = ""
    desc: Optional[str] = ""
    displayable: Optional[str] = ""
    payload: Optional[List[WorkflowPayloadVO]] = None
    status: Optional[str] = ""
    type: Optional[str] = ""
    model_config = {
        "extra": "ignore"
    }

class WorkflowEventListVO(BaseModel):
    systemEvents: Optional[List[WorkflowEventVO]] = None
    customEvents: Optional[List[WorkflowEventVO]] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class WorkflowActivityTypeListVO(BaseModel):
    activityTypes: Optional[List[str]] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class WorkflowActivityVO(BaseModel):
    id: Optional[str] = ""
    categoryId: Optional[str] = ""
    desc: Optional[str] = ""
    displayable: Optional[str] = ""
    name: Optional[str] = ""
    inputs: Optional[List[WorkflowInputsVO]] = None
    outputs: Optional[List[WorkflowOutputsVO]] = None
    status: Optional[str] = ""
    model_config = {
        "extra": "ignore"
    }

class WorkflowActivityListVO(BaseModel):
    activities: Optional[List[WorkflowActivityVO]] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }

class WorkflowConditionVO(BaseModel):
    id: Optional[str] = ""
    categoryId: Optional[str] = ""
    desc: Optional[str] = ""
    name: Optional[str] = ""
    displayable: Optional[str] = ""
    inputs: Optional[List[WorkflowInputsVO]] = None
    outputs: Optional[List[WorkflowOutputsVO]] = None
    status: Optional[str] = ""
    model_config = {
        "extra": "ignore"
    }

class WorkflowConditionListVO(BaseModel):
    conditions: Optional[List[WorkflowConditionVO]] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }

class WorkflowTaskInputsVO(BaseModel):
    name: Optional[str] = ""
    description: Optional[str] = ""
    dataType: Optional[str] = ""
    required: Optional[bool] = False
    model_config = {
        "extra": "ignore"
    }

class WorkflowTaskOutputsVO(BaseModel):
    name: Optional[str] = ""
    description: Optional[str] = ""
    dataType: Optional[str] = ""
    model_config = {
        "extra": "ignore"
    }

class WorkflowTaskVO(BaseModel):
    id: Optional[str] = ""
    name: Optional[str] = ""
    displayable: Optional[str] = ""
    description: Optional[str] = ""
    inputs: Optional[List[WorkflowTaskInputsVO]] = None
    outputs: Optional[List[WorkflowTaskOutputsVO]] = None
    model_config = {
        "extra": "ignore"
    }

class WorkflowTaskListVO(BaseModel):
    tasks: Optional[List[WorkflowTaskVO]] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }

class WorkflowRuleInputsVO(BaseModel):
    name: Optional[str] = ""
    description: Optional[str] = ""
    type: Optional[str] = ""
    isrequired: Optional[bool] = False
    format: Optional[str] = ""
    model_config = {
        "extra": "ignore"
    }

class WorkflowRuleOutputsVO(BaseModel):
    name: Optional[str] = ""
    description: Optional[str] = ""
    type: Optional[str] = ""
    format: Optional[str] = ""
    model_config = {
        "extra": "ignore"
    }

class WorkflowRuleVO(BaseModel):
    id: Optional[str] = ""
    name: Optional[str] = ""
    description: Optional[str] = ""
    ruleInputs: Optional[List[WorkflowRuleInputsVO]] = None
    ruleOutputs: Optional[List[WorkflowRuleOutputsVO]] = None
    appScopeName: Optional[str] = ""
    model_config = {
        "extra": "ignore"
    }

class WorkflowRuleListVO(BaseModel):
    rules: Optional[List[WorkflowRuleVO]] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }

class WorkflowPredefinedVariableVO(BaseModel):
    id: Optional[str] = ""
    type: Optional[str] = ""
    name: Optional[str] = ""
    desc: Optional[str] = ""

class WorkflowPredefinedVariableListVO(BaseModel):
    items: Optional[List[WorkflowPredefinedVariableVO]] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }

class EventPayloadTypeEnum(str, Enum):
    Text = "Text"
    MultilineText = "MultilineText"
    TextArray = "TextArray"
    DynamicTextArray = "DynamicTextArray"
    Number = "Number"
    File = "File"
    Boolean = "Boolean"
    Json = "Json"

class WorkflowCustomEventPayloadVO(BaseModel):
    name: str
    desc: str
    type: EventPayloadTypeEnum
    model_config = {
        "extra": "ignore"
    }

class WorkflowCustomEventCreateVO(BaseModel):
    displayable: str
    desc: str
    categoryId: str
    payload: List[WorkflowCustomEventPayloadVO]
    type: str = "CUSTOM_EVENT"
    model_config = {
        "extra": "ignore"
    }

class TaskReadmeResponseVO(BaseModel):
    readmeText: Optional[str] = ""
    taskName: Optional[str] = ""
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }

class RuleReadmeResponseVO(BaseModel):
    readmeText: Optional[str] = ""
    ruleName: Optional[str] = ""
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class WorkflowResourceDataVO(BaseModel):
    items: Optional[List[Any]] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class WorkflowCreateResponseVO(BaseModel):
    workflowId: Optional[str] = ""
    uiUrl: Optional[str] = ""
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class WorkflowListResponseVO(BaseModel):
    items: Optional[List[Any]] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class WorkflowItemResponseVO(BaseModel):
    item: Optional[Any] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class WorkflowMutationResponseVO(BaseModel):
    success: Optional[bool] = False
    message: Optional[Any] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class WorkflowCustomEventResponseVO(BaseModel):
    id: Optional[str] = ""
    preview: Optional[Any] = None
    next_step: Optional[str] = ""
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class WorkflowTriggerResponseVO(BaseModel):
    message: Optional[str] = ""
    event: Optional[str] = ""
    requiredInputs: Optional[List[str]] = None
    provided: Optional[dict[str, Any]] = None
    missing: Optional[List[str]] = None
    next_step: Optional[str] = ""
    result: Optional[Any] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }

from pydantic import BaseModel, Field
from typing import List, Optional, Any
from mcptypes.error_type import StructuredError

class AutomatedControlVO(BaseModel):
    id: Optional[str] = ""
    displayable: Optional[str] = ""
    alias: Optional[str] = ""
    activationStatus: Optional[str] = ""
    ruleName: Optional[str] = ""
    assessmentId: Optional[str] = ""
    model_config = {
        "extra": "ignore"
    }
    
class AutomatedControlListVO(BaseModel):
    controls: Optional[List[AutomatedControlVO]] = None
    error: Optional[StructuredError] = None
    model_config = {
        "extra": "ignore"
    }

class ActionsVO(BaseModel):
    actionName: Optional[str] = ""
    actionDescription: Optional[str] = ""
    actionSpecID: Optional[str] = ""
    actionBindingID: Optional[str] = ""
    target: Optional[str] = ""
    ruleInputs: Optional[dict[str, Any]] = None
    
    model_config = {
        "extra": "ignore"
    }

class ActionsListVO(BaseModel):
    actions: Optional[List[ActionsVO]] = None
    error: Optional[StructuredError] = None
    

class RecordsVO(BaseModel):
    id: Optional[str] = ""
    name: Optional[str] = Field(default="", validation_alias="System")
    source: Optional[str] = Field(default="", validation_alias="Source")
    resourceId: Optional[str] = Field(default="", validation_alias="ResourceID")
    resourceName: Optional[str] = Field(default="", validation_alias="ResourceName")
    resourceType: Optional[str] = Field(default="", validation_alias="ResourceType")
    complianceStatus: Optional[str] = Field(default="", validation_alias="ComplianceStatus")
    complianceReason: Optional[str] = Field(default="", validation_alias="ComplianceReason")
    createdAt: Optional[str] = Field(default="", validation_alias="CreatedAt")
    otherInfo : Optional[Any] = None
    
    model_config = {
        "extra": "ignore"
    }
    
class RecordListVO(BaseModel):
    totalRecords:  Optional[int] = 0
    compliantRecords:  Optional[int] = 0
    nonCompliantRecords:  Optional[int] = 0
    notDeterminedRecords:  Optional[int] = 0
    records:  Optional[List[Any]] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }

class RecordSchemaVO(BaseModel):
    name: Optional[str] = ""
    type: Optional[str] = ""
    model_config = {
        "extra": "ignore"
    }
    

class RecordSchemaListVO(BaseModel):
    recordSchema: Optional[List[RecordSchemaVO]] = None
    error: Optional[StructuredError] = None

class ControlPromptVO(BaseModel):
    prompt:  Optional[str] = ""
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }


class ControlMetadataVO(BaseModel):
    assessementId: Optional[str] = Field(default="", validation_alias="planId")
    assessmentName: Optional[str] = Field(default="", validation_alias="planName")
    assessmentRunId: Optional[str] = Field(default="", validation_alias="planInstanceId")
    assessmentRunName: Optional[str] = Field(default="", validation_alias="planInstanceName")
    controlId: Optional[str] = Field(default="", validation_alias="planInstanceControlId")
    controlName: Optional[str] = Field(default="", validation_alias="planInstanceControlName")
    controlNumber: Optional[str] = Field(default="", validation_alias="planInstanceControlDisplayable")
    error: Optional[StructuredError] = None
    
    model_config = {
        "extra": "ignore"
    }

# @dataclass
class ControlVO(BaseModel):
    id: Optional[str] = ""
    name: Optional[str] = ""
    controlNumber: Optional[str] = Field(default="", validation_alias="displayable")
    alias: Optional[str] = ""
    priority: Optional[str] = ""
    stage: Optional[str] = ""
    status: Optional[str] = ""
    type: Optional[str] = ""
    executionStatus: Optional[str] = ""
    dueDate: Optional[str] = ""
    assignedTo: Optional[List[str]] = Field(default_factory=list)
    assignedBy: Optional[str] = ""
    assignedDate: Optional[str] = ""
    checkedOut: Optional[bool] = False
    compliancePCT__: Optional[float] = 0.0
    complianceWeight__: Optional[float] = 0.0
    complianceStatus: Optional[str] = ""
    createdAt: Optional[str] = ""
    updatedAt: Optional[str] = ""
    
    model_config = {
        "extra": "ignore"
    }
    
# @dataclass
class ControlListVO(BaseModel):
    controls: Optional[List[ControlVO]] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }

class AssessmentRunVO(BaseModel):
    id: Optional[str] = ""
    name: Optional[str] = ""
    description: Optional[str] = ""
    assessmentId: Optional[str] = ""
    applicationType: Optional[str] = ""
    configId: Optional[str] = ""
    fromDate: Optional[str] = ""
    toDate: Optional[str] = ""
    # started: Optional[str] = ""
    ended: Optional[str] = ""
    status: Optional[str] = ""
    computedScore: Optional[float] = 0
    computedWeight: Optional[float] = 0
    complianceStatus: Optional[str] = ""
    compliancePCT: Optional[float] = 0.0
    complianceWeight: Optional[float] = 0.0
    createdAt: Optional[str] = ""

    model_config = {
        "extra": "ignore"
    }

class AssessmentRunListVO(BaseModel):
    assessmentRuns: Optional[List[AssessmentRunVO]] = None
    error: Optional[StructuredError] = None


    model_config = {
        "extra": "ignore"
    }
    
    
class ControlEvidenceVO(BaseModel):
    id: Optional[str] = ""
    name: Optional[str] = ""
    description: Optional[str] = ""
    fileName: Optional[str] = ""
    model_config = {
        "extra": "ignore"
    }
    
class ControlEvidenceListVO(BaseModel):
    evidences: Optional[List[ControlEvidenceVO]] = None
    error: Optional[StructuredError] = None
    


class TriggerActionVO(BaseModel):
    id: Optional[str] = ""
    message: Optional[str] = ""
    error: Optional[StructuredError] = None
    
    model_config = {
        "extra": "ignore"
    }


class UploadEvidenceVO(BaseModel):
    id: Optional[str] = ""
    message: Optional[str] = ""
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore"
    }

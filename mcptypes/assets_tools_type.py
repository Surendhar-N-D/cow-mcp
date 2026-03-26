from pydantic import BaseModel, Field
from dataclasses import dataclass, field
from typing import List, Optional, Any
from mcptypes.error_type import StructuredError

class ResourceTypeVO(BaseModel):
    resourceType: Optional[str] = ""
    totalResources: Optional[int] = 0
    model_config = {
        "extra": "ignore"
    }
class ResourceTypeListVO(BaseModel):
    resourceTypes: Optional[List[ResourceTypeVO]] = None
    error: Optional[StructuredError] = None
    
class ResourceTypeSummaryVO(BaseModel):
    resourcesTypes: Optional[List[ResourceTypeVO]] = None
    totalItems: Optional[int]= 0
    error: Optional[StructuredError] = None

class AssetVO(BaseModel):
    id: Optional[str] = ""
    name: Optional[str] = ""
    
    model_config = {
        "extra": "ignore"
    }
class AssetListVO(BaseModel):
    assets: Optional[List[AssetVO]] = None
    error: Optional[StructuredError] = None
    
class NumberOfChecks(BaseModel):
    COMPLIANT: Optional[int] = 0
    NON_COMPLIANT: Optional[int] = 0
    
class AssestsSummaryVO(BaseModel):
    integrationRunId: Optional[str] = Field(default="", validation_alias="planRunID")
    assessmentName: Optional[str] = ""
    status: Optional[str] = ""
    numberOfResources: Optional[int] = None
    numberOfChecks: Optional[NumberOfChecks] = None
    dataStatus: Optional[str] = ""
    createdAt: Optional[str] = ""
    error: Optional[StructuredError] = None
    
    model_config = {
        "extra": "ignore"
    }
    
class RuleVO(BaseModel):
    type: Optional[str] = ""
    name: Optional[str] = ""
    

class CheckVO(BaseModel):
    name: Optional[str] = ""
    description: Optional[str] = ""
    rule: Optional[RuleVO] = None
    activationStatus: Optional[str] = ""
    priority: Optional[str] = ""
    complianceStatus: Optional[str] = ""
    compliancePCT: Optional[float] = 0
    model_config = {
        "extra": "ignore"
    }
    
class ChecksListVO(BaseModel):
    checks: Optional[List[CheckVO]] = None
    page: Optional[int] = 0
    totalPage: Optional[int] = 0
    totalItems: Optional[int] = 0
    error: Optional[StructuredError] = None
    
class CheckSummaryVO(BaseModel):
    complianceSummary: Optional[Any] = None
    error: Optional[StructuredError] = None
    
class ResourceSummaryVO(BaseModel):
    complianceSummary: Optional[Any] = None
    error: Optional[StructuredError] = None

class ResourceCheckVO(BaseModel):
    name: Optional[str] = ""
    description: Optional[str] = ""
    rule: Optional[RuleVO] = None
    activationStatus: Optional[str] = ""
    priority: Optional[str] = ""
    controlName: Optional[str] = ""
    complianceStatus: Optional[str] = Field(default="", validation_alias="resourceComplianceStatus")
    
    model_config = {
        "extra": "ignore"
    }
    
class ResourceVO(BaseModel):
    name: Optional[str] = ""
    resourceType: Optional[str] = ""
    complianceStatus: Optional[str] = ""
    checks: Optional[List[ResourceCheckVO]] = None
    model_config = {
        "extra": "ignore"
    }
    
class ResourceListVO(BaseModel):
    resources: Optional[List[ResourceVO]] = None
    page: Optional[int] = 0
    totalPage: Optional[int] = 0
    totalItems: Optional[int] = 0
    error: Optional[StructuredError] = None
    
    

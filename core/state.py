from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum

class DocumentStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    VERIFIED = "VERIFIED"
    FLAGGED = "FLAGGED"
    FAILED = "FAILED"

class AuditState(BaseModel):
    company_id : Optional[str] = None
    document_id : Optional[str] = None

    file_path : Optional[str] = None
    file_type : Optional[str] = None

    document_type : Optional[str] = None
    classification_confidence : Optional[float] = None

    parced_content : Optional[Any] = None
    extraced_data : Optional[dict[str, Any]] = None

    validation_results : Dict[str, Any] = Field(default_factory= dict)
    ml_signals : Dict[str, Any] = Field(default_factory= dict)

    retry_count : int = 0
    status : DocumentStatus = DocumentStatus.IN_PROGRESS

    audit_trace : List[str] = Field(default_factory=list)


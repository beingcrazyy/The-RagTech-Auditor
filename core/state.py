from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
from core.enums.document_status import DocumentStatus

class AuditState(BaseModel):
    company_id : Optional[str] = None
    document_id : Optional[str] = None

    file_path : Optional[str] = None
    file_type : Optional[str] = None

    document_type : Optional[str] = None
    classification_confidence : Optional[float] = None

    parsed_content : Optional[Dict[str, Any]] = None
    extraced_data : Optional[dict[str, Any]] = None

    validation_results : Dict[str, Any] = Field(default_factory= dict)
    ml_signals : Dict[str, Any] = Field(default_factory= dict)

    retry_count : int = 0
    status : Optional[DocumentStatus] = None
    audit_summary : Optional[str] = None


    audit_trace : List[str] = Field(default_factory=list)


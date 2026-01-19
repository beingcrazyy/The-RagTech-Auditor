from enum import Enum

class DocumentStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    VERIFIED = "VERIFIED"
    FLAGGED = "FLAGGED"
    FAILED = "FAILED"
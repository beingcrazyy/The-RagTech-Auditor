from enum import Enum

class DocumentResults(str, Enum):
    VERIFIED = "VERIFIED"
    FLAGGED = "FLAGGED"
    FAILED = "FAILED"
    OUT_OF_SCOPE = "OUT OF SCOPE"
from enum import Enum

class DocumentType(str, Enum):
    INVOICE = "INVOICE"
    BANK_STATEMENT = "BANK_STATEMENT"
    P_AND_L = "P_AND_L"
    OTHER = "OTHER"
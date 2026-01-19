from enum import Enum

class FileType(str, Enum):
    PDF = "PDF"
    IMAGE = "IMAGE"
    EXCEL = "EXCEL"
    OTHER = "OTHER"
    
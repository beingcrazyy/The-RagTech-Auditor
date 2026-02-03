from services.llm.runner import run_llm
from services.llm.prompts.document_classification import (
    build_document_classification_prompt
)
from core.enums.document_type import DocumentType
from config.logger import get_logger

logger = get_logger(__name__)

def llm_document_classifier(text: str) -> DocumentType:
    """
    Classify document using LLM.
    Returns a DocumentType enum.
    """

    prompt = build_document_classification_prompt(text)

    logger.info("Running LLM-based document classification")

    result = run_llm(
        prompt=prompt,
        temperature=0
    )

    normalized = result.strip().upper()

    try:
        return DocumentType[normalized]
    except KeyError:
        logger.warning(
            f"LLM returned unknown document type '{normalized}', defaulting to OTHER"
        )
        return DocumentType.OTHER
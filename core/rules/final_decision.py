from core.enums.document_results import DocumentResults

def decide_final_status(validation_results : dict, ml_signals : dict | None = None) -> DocumentResults:
    
    hard = validation_results.get("hard_failures", [])
    soft = validation_results.get("soft_failures", [])

    if hard:
        return DocumentResults.FAILED
    if soft:
        return DocumentResults.FLAGGED
    
    if ml_signals:
        risk = ml_signals.get("risk_score", 0)
        if risk > 0.7 :
            return DocumentResults.FLAGGED

    return DocumentResults.VERIFIED

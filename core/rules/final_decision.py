from core.enums.document_status import DocumentStatus

def decide_final_status(validation_results : dict, ml_signals : dict | None = None) -> DocumentStatus:
    
    hard = validation_results.get("hard_failures", [])
    soft = validation_results.get("soft_failures", [])

    if hard:
        return DocumentStatus.FAILED
    if soft:
        return DocumentStatus.FLAGGED
    
    if ml_signals:
        risk = ml_signals.get("risk_score", 0)
        if risk > 0.7 :
            return DocumentStatus.FLAGGED

    return DocumentStatus.VERIFIED

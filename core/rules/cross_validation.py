from typing import Dict, Optional, List

def emit(rule_id: str, message: str, evidence_ref: str, confidence: float = 1.0) -> Dict:
    return {
        "rule_id": rule_id,
        "message": message,
        "evidence_ref": evidence_ref,
        "confidence": confidence
    }



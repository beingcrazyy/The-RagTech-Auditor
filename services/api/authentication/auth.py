from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional
from config.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
async def login(req: LoginRequest):
    email = req.email.strip()
    password = req.password.strip()
    
    logger.info(f"Login attempt for email: {email}")
    
    # Mock authentication logic
    if email == "1@2" and password == "123":
        logger.info(f"Login successful for {email}")
        return {
            "user_id": "user_001",
            "name": "Admin User",
            "token": "mock_jwt_token_for_demo_purposes"
        }
    elif email == "auditor@ragtech.com" and password == "password":
        logger.info(f"Login successful for {email}")
        return {
            "user_id": "user_002",
            "name": "RegTech Auditor",
            "token": "mock_jwt_token_for_auditor"
        }
    else:
        logger.warning(f"Login failed for {email}, {password}: Invalid credentials")
        raise HTTPException(status_code=401, detail="Invalid email or password")

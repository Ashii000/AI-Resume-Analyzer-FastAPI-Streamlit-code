"""AI integrations endpoints (placeholder)"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/ping")
async def ping():
    return {"msg": "ai api placeholder"}

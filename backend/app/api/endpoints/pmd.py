import os
from fastapi import APIRouter, HTTPException
from app.models.pmd import PmdResult
from app.services.pmd_service import run_pmd_analysis
from app.core.config import settings

router = APIRouter()


@router.get("/analysis/{full_path:path}", response_model=PmdResult)
async def api_pmd_analysis(full_path: str):
    full_path = os.path.abspath(full_path)
    if not full_path.startswith(settings.BACKEND_DIR):
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        result = run_pmd_analysis(full_path)
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

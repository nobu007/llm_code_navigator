from fastapi import APIRouter, HTTPException
from app.models.file import FileData, FileContent
from app.services.file_service import get_file_data, get_file_content
from app.core.config import settings
import os

router = APIRouter()

@router.get("/files_info", response_model=FileData)
async def api_get_files_info():
    print("api_get_files_info settings.BACKEND_DIR=",settings.BACKEND_DIR)
    try:
        return get_file_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/file_content/{full_path:path}", response_model=FileContent)
async def api_get_file_content(full_path: str):
    # ベースディレクトリ外のアクセスを防止
    print("api_get_file_content settings.BACKEND_DIR=",settings.BACKEND_DIR)
    print("api_get_file_content full_path=",full_path)
    full_path=os.path.abspath(full_path)
    if not full_path.startswith(settings.BACKEND_DIR):
        raise HTTPException(status_code=403, detail="Access denied(not in BACKEND_DIR)")

    try:
        content = get_file_content(full_path)
        return FileContent(content=content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except PermissionError:
        raise HTTPException(status_code=403, detail="Access denied")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
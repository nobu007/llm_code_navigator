from fastapi import APIRouter, HTTPException
from app.models.file import FileData, FileContent
from app.services.file_service import get_files_info, get_file_content

router = APIRouter()

@router.get("/files_info", response_model=FileData)
async def api_get_files_info():
    try:
        return get_files_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/file_content/{file_path:path}", response_model=FileContent)
async def api_get_file_content(file_path: str):
    try:
        content = get_file_content(file_path)
        return FileContent(content=content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except PermissionError:
        raise HTTPException(status_code=403, detail="Access denied")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
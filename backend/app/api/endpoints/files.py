from fastapi import APIRouter, HTTPException
from app.models.file import FileData, FileContent
from app.services.file_service import get_file_data, get_file_content

router = APIRouter()

@router.get("", response_model=FileData)
async def get_files():
    try:
        return get_file_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{file_path:path}", response_model=FileContent)
async def read_file_content(file_path: str):
    try:
        content = get_file_content(file_path)
        return FileContent(content=content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except PermissionError:
        raise HTTPException(status_code=403, detail="Access denied")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
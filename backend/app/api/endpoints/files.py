from fastapi import APIRouter, HTTPException
from app.models.file import FileData, FileContent
from app.services.file_service import get_file_data, get_file_content
from app.core.config import settings
import os

router = APIRouter()


@router.get("/files_info", response_model=FileData)
async def api_get_files_info():
    """Get file information and relationships."""
    print("api_get_files_info settings.BACKEND_DIR=", settings.BACKEND_DIR)
    try:
        file_data = get_file_data()
        return file_data
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Directory not found: {str(e)}")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=f"Access denied: {str(e)}")
    except Exception as e:
        print(f"Error in api_get_files_info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/file_content/{full_path:path}", response_model=FileContent)
async def api_get_file_content(full_path: str):
    """
    Retrieve file content with secure path validation and proper encoding handling.
    
    Args:
        full_path: Path to the file to retrieve content from
        
    Returns:
        FileContent: Object containing file content, path, and encoding information
        
    Raises:
        HTTPException: 403 for access denied, 404 for file not found, 500 for server errors
    """
    print("api_get_file_content settings.BACKEND_DIR=", settings.BACKEND_DIR)
    print("api_get_file_content full_path=", full_path)
    
    try:
        # The file service now handles all path validation and security checks
        file_content = get_file_content(full_path)
        return file_content
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=f"Access denied: {str(e)}")
    except UnicodeDecodeError as e:
        raise HTTPException(status_code=422, detail=f"File encoding error: {str(e)}")
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"File system error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

from pydantic import BaseModel
from typing import List, Optional


class FileNode(BaseModel):
    id: str
    name: str
    type: str
    children: Optional[List['FileNode']] = None


class FileEdge(BaseModel):
    source: str
    target: str


class FileData(BaseModel):
    files: List[FileNode]
    relationships: List[FileEdge]


class FileContent(BaseModel):
    content: str


class FilePath(BaseModel):
    full: str  # full path
    base: str  # base path(settings.BACKEND_DIR)
    relative: str  # relative path

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal


class FileNode(BaseModel):
    id: str = Field(..., description="Unique identifier for the file node")
    name: str = Field(..., description="Name of the file or directory")
    type: Literal['file', 'directory'] = Field(..., description="Type of the node")
    children: Optional[List['FileNode']] = Field(None, description="Child nodes for directories")

    @validator('id')
    def validate_id(cls, v):
        if not v or not v.strip():
            raise ValueError('ID cannot be empty')
        return v.strip()

    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


class FileEdge(BaseModel):
    source: str = Field(..., description="Source file ID in the relationship")
    target: str = Field(..., description="Target file ID in the relationship")

    @validator('source', 'target')
    def validate_node_ids(cls, v):
        if not v or not v.strip():
            raise ValueError('Node ID cannot be empty')
        return v.strip()


class FileData(BaseModel):
    files: List[FileNode] = Field(..., description="List of file nodes in the codebase")
    relationships: List[FileEdge] = Field(..., description="List of dependency relationships between files")


class FileContent(BaseModel):
    content: str = Field(..., description="Content of the file")
    path: str = Field(..., description="Path to the file")
    encoding: str = Field(default="utf-8", description="File encoding")

    @validator('path')
    def validate_path(cls, v):
        if not v or not v.strip():
            raise ValueError('Path cannot be empty')
        return v.strip()


class FilePath(BaseModel):
    full: str = Field(..., description="Full absolute path")
    base: str = Field(..., description="Base path (settings.BACKEND_DIR)")
    relative: str = Field(..., description="Relative path from base")

    @validator('full', 'base', 'relative')
    def validate_paths(cls, v):
        if not v or not v.strip():
            raise ValueError('Path cannot be empty')
        return v.strip()

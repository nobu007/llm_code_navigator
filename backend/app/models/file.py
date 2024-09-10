from pydantic import BaseModel
from typing import List

class FileNode(BaseModel):
    id: str
    label: str

class FileEdge(BaseModel):
    source: str
    target: str

class FileData(BaseModel):
    nodes: List[FileNode]
    edges: List[FileEdge]

class FileContent(BaseModel):
    content: str
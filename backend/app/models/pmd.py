from pydantic import BaseModel
from typing import Any


class PmdResult(BaseModel):
    result: Any

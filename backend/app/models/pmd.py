from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any


class PmdViolation(BaseModel):
    rule: str = Field(..., description="PMD rule that was violated")
    priority: int = Field(..., description="Priority level of the violation")
    message: str = Field(..., description="Description of the violation")
    line: int = Field(..., description="Line number where violation occurred")
    column: int = Field(..., description="Column number where violation occurred")

    @validator('rule', 'message')
    def validate_strings(cls, v):
        if not v or not v.strip():
            raise ValueError('Rule and message cannot be empty')
        return v.strip()

    @validator('priority')
    def validate_priority(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Priority must be between 1 and 5')
        return v

    @validator('line', 'column')
    def validate_position(cls, v):
        if v < 0:
            raise ValueError('Line and column numbers must be non-negative')
        return v


class PmdResult(BaseModel):
    violations: List[PmdViolation] = Field(..., description="List of code violations found by PMD")
    summary: Dict[str, Any] = Field(..., description="Summary information about the analysis")

    @validator('summary')
    def validate_summary(cls, v):
        if not isinstance(v, dict):
            raise ValueError('Summary must be a dictionary')
        return v

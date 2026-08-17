"""Pydantic request and response models for calculator routes."""

from math import isfinite

from pydantic import BaseModel, field_validator


class OperandRequest(BaseModel):
    """JSON body with two finite numeric operands."""

    a: float
    b: float

    @field_validator("a", "b")
    @classmethod
    def must_be_finite(cls, value: float) -> float:
        """Reject inf and nan so they return HTTP 422."""
        if not isfinite(value):
            raise ValueError("must be a finite number")
        return value


class CalculationResult(BaseModel):
    """Successful calculation response."""

    operation: str
    a: float
    b: float
    result: float

"""Pydantic request and response models for calculator routes."""

from math import isfinite

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _must_be_finite(value: float) -> float:
    """Reject inf and nan so they return HTTP 422."""
    if not isfinite(value):
        raise ValueError("must be a finite number")
    return value


class OperandRequest(BaseModel):
    """JSON body with two finite numeric operands."""

    a: float
    b: float

    @field_validator("a", "b")
    @classmethod
    def must_be_finite(cls, value: float) -> float:
        """Reject inf and nan so they return HTTP 422."""
        return _must_be_finite(value)


class UnaryOperandRequest(BaseModel):
    """JSON body with one finite numeric operand."""

    a: float

    @field_validator("a")
    @classmethod
    def must_be_finite(cls, value: float) -> float:
        """Reject inf and nan so they return HTTP 422."""
        return _must_be_finite(value)


class CalculationResult(BaseModel):
    """Successful calculation response."""

    operation: str
    a: float
    b: float | None = None
    result: float


class MemoryValueRequest(BaseModel):
    """JSON body for M+ / M− with one finite number."""

    value: float

    @field_validator("value")
    @classmethod
    def must_be_finite(cls, value: float) -> float:
        """Reject inf and nan so they return HTTP 422."""
        return _must_be_finite(value)


class HistoryEntryModel(BaseModel):
    """One recorded calculation on the history tape."""

    operation: str
    a: float
    b: float | None = None
    result: float
    at: str


class MemorySnapshot(BaseModel):
    """Current M register and calculation history."""

    model_config = ConfigDict(populate_by_name=True)

    stored_value: float = Field(
        validation_alias="register",
        serialization_alias="register",
    )
    history: list[HistoryEntryModel]

"""HTTP routes for calculator operations."""

from fastapi import APIRouter, HTTPException

from calc_app.api.schemas import CalculationResult, OperandRequest
from calc_app.calculator import add, divide, multiply, subtract

router = APIRouter()


@router.post("/add", response_model=CalculationResult)
def add_numbers(payload: OperandRequest) -> CalculationResult:
    """Add two numbers."""
    return CalculationResult(
        operation="add",
        a=payload.a,
        b=payload.b,
        result=add(payload.a, payload.b),
    )


@router.post("/subtract", response_model=CalculationResult)
def subtract_numbers(payload: OperandRequest) -> CalculationResult:
    """Subtract b from a."""
    return CalculationResult(
        operation="subtract",
        a=payload.a,
        b=payload.b,
        result=subtract(payload.a, payload.b),
    )


@router.post("/multiply", response_model=CalculationResult)
def multiply_numbers(payload: OperandRequest) -> CalculationResult:
    """Multiply two numbers."""
    return CalculationResult(
        operation="multiply",
        a=payload.a,
        b=payload.b,
        result=multiply(payload.a, payload.b),
    )


@router.post("/divide", response_model=CalculationResult)
def divide_numbers(payload: OperandRequest) -> CalculationResult:
    """Divide a by b. Returns 400 when b is zero."""
    try:
        result = divide(payload.a, payload.b)
    except ZeroDivisionError as exc:
        raise HTTPException(status_code=400, detail="Division by zero") from exc
    return CalculationResult(
        operation="divide",
        a=payload.a,
        b=payload.b,
        result=result,
    )

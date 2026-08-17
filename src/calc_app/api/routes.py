"""HTTP routes for calculator operations."""

from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from calc_app.api.schemas import (
    CalculationResult,
    HistoryEntryModel,
    MemorySnapshot,
    MemoryValueRequest,
    OperandRequest,
    UnaryOperandRequest,
)
from calc_app.calculator import add, divide, multiply, sqrt, subtract
from calc_app.memory import MemoryStore

router = APIRouter()


def get_store(request: Request) -> MemoryStore:
    """Return the process-wide memory store from app state."""
    return request.app.state.memory_store


StoreDep = Annotated[MemoryStore, Depends(get_store)]


def _snapshot(store: MemoryStore) -> MemorySnapshot:
    snap = store.snapshot()
    return MemorySnapshot(
        stored_value=snap.register,
        history=[HistoryEntryModel.model_validate(asdict(entry)) for entry in snap.history],
    )


def _recorded_result(
    store: MemoryStore,
    operation: str,
    a: float,
    b: float | None,
    result: float,
) -> CalculationResult:
    store.record(operation, a, b, result)
    return CalculationResult(operation=operation, a=a, b=b, result=result)


@router.post("/add", response_model=CalculationResult)
def add_numbers(payload: OperandRequest, store: StoreDep) -> CalculationResult:
    """Add two numbers."""
    return _recorded_result(store, "add", payload.a, payload.b, add(payload.a, payload.b))


@router.post("/subtract", response_model=CalculationResult)
def subtract_numbers(payload: OperandRequest, store: StoreDep) -> CalculationResult:
    """Subtract b from a."""
    return _recorded_result(store, "subtract", payload.a, payload.b, subtract(payload.a, payload.b))


@router.post("/multiply", response_model=CalculationResult)
def multiply_numbers(payload: OperandRequest, store: StoreDep) -> CalculationResult:
    """Multiply two numbers."""
    return _recorded_result(store, "multiply", payload.a, payload.b, multiply(payload.a, payload.b))


@router.post("/divide", response_model=CalculationResult)
def divide_numbers(payload: OperandRequest, store: StoreDep) -> CalculationResult:
    """Divide a by b. Returns 400 when b is zero."""
    try:
        result = divide(payload.a, payload.b)
    except ZeroDivisionError as exc:
        raise HTTPException(status_code=400, detail="Division by zero") from exc
    return _recorded_result(store, "divide", payload.a, payload.b, result)


@router.post("/sqrt", response_model=CalculationResult)
def sqrt_number(payload: UnaryOperandRequest, store: StoreDep) -> CalculationResult:
    """Return the square root of a. Returns 400 when a is negative."""
    try:
        result = sqrt(payload.a)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Square root of negative number") from exc
    return _recorded_result(store, "sqrt", payload.a, None, result)


@router.get("/memory", response_model=MemorySnapshot)
def read_memory(store: StoreDep) -> MemorySnapshot:
    """Return the M register and calculation history."""
    return _snapshot(store)


@router.post("/memory/plus", response_model=MemorySnapshot)
def memory_plus(payload: MemoryValueRequest, store: StoreDep) -> MemorySnapshot:
    """Add a value to the memory register (M+)."""
    store.plus(payload.value)
    return _snapshot(store)


@router.post("/memory/minus", response_model=MemorySnapshot)
def memory_minus(payload: MemoryValueRequest, store: StoreDep) -> MemorySnapshot:
    """Subtract a value from the memory register (M−)."""
    store.minus(payload.value)
    return _snapshot(store)


@router.delete("/memory/register", response_model=MemorySnapshot)
def clear_memory_register(store: StoreDep) -> MemorySnapshot:
    """Clear the memory register (MC). History is unchanged."""
    store.clear_register()
    return _snapshot(store)


@router.delete("/memory/history", response_model=MemorySnapshot)
def clear_memory_history(store: StoreDep) -> MemorySnapshot:
    """Clear the calculation history tape. Register is unchanged."""
    store.clear_history()
    return _snapshot(store)

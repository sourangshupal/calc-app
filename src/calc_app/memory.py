"""Persistent calculator memory: M register plus calculation history."""

from __future__ import annotations

import json
import threading
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def default_memory_path() -> Path:
    """Return the default JSON file path under the project data directory."""
    return Path(__file__).resolve().parents[2] / "data" / "memory.json"


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class HistoryEntry:
    """One successful calculation stored on the history tape."""

    operation: str
    a: float
    b: float
    result: float
    at: str


@dataclass(frozen=True)
class MemoryState:
    """Snapshot of the M register and history tape."""

    register: float
    history: list[HistoryEntry]


class MemoryStore:
    """Thread-safe JSON-backed memory for register and calculation history."""

    def __init__(self, path: Path, max_history: int = 100) -> None:
        """Create a store backed by ``path``.

        Args:
            path: JSON file used for persistence.
            max_history: Maximum number of newest history entries to keep.
        """
        self._path = path
        self._max_history = max_history
        self._lock = threading.Lock()
        self._register = 0.0
        self._history: list[HistoryEntry] = []
        self._load()

    def snapshot(self) -> MemoryState:
        """Return a copy of the current register and history."""
        with self._lock:
            return MemoryState(register=self._register, history=list(self._history))

    def plus(self, value: float) -> float:
        """Add ``value`` to the memory register (M+) and persist."""
        with self._lock:
            self._register += value
            self._save_unlocked()
            return self._register

    def minus(self, value: float) -> float:
        """Subtract ``value`` from the memory register (M−) and persist."""
        with self._lock:
            self._register -= value
            self._save_unlocked()
            return self._register

    def clear_register(self) -> None:
        """Reset the memory register to zero (MC) and persist."""
        with self._lock:
            self._register = 0.0
            self._save_unlocked()

    def record(self, operation: str, a: float, b: float, result: float) -> HistoryEntry:
        """Append a successful calculation to the tape and persist.

        Args:
            operation: Name of the arithmetic operation.
            a: Left operand.
            b: Right operand.
            result: Computed result.

        Returns:
            The stored history entry, including a UTC timestamp.
        """
        entry = HistoryEntry(
            operation=operation,
            a=a,
            b=b,
            result=result,
            at=_utc_now(),
        )
        with self._lock:
            self._history.append(entry)
            if len(self._history) > self._max_history:
                self._history = self._history[-self._max_history :]
            self._save_unlocked()
        return entry

    def clear_history(self) -> None:
        """Wipe the history tape. Leaves the register unchanged."""
        with self._lock:
            self._history = []
            self._save_unlocked()

    def _load(self) -> None:
        if not self._path.exists():
            return
        raw = json.loads(self._path.read_text(encoding="utf-8"))
        self._register = float(raw.get("register", 0.0))
        self._history = [
            HistoryEntry(
                operation=str(item["operation"]),
                a=float(item["a"]),
                b=float(item["b"]),
                result=float(item["result"]),
                at=str(item["at"]),
            )
            for item in raw.get("history", [])
        ]
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history :]

    def _save_unlocked(self) -> None:
        payload: dict[str, Any] = {
            "register": self._register,
            "history": [asdict(entry) for entry in self._history],
        }
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

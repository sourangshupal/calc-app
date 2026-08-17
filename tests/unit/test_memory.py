"""Unit tests for the persistent calculator memory store."""

from pathlib import Path

from calc_app.memory import MemoryStore


def test_empty_store_has_zero_register_and_no_history(tmp_path: Path) -> None:
    store = MemoryStore(tmp_path / "memory.json")
    snap = store.snapshot()
    assert snap.register == 0.0
    assert snap.history == []


def test_plus_adds_to_register(tmp_path: Path) -> None:
    store = MemoryStore(tmp_path / "memory.json")
    assert store.plus(5.0) == 5.0
    assert store.plus(2.5) == 7.5
    assert store.snapshot().register == 7.5


def test_minus_subtracts_from_register(tmp_path: Path) -> None:
    store = MemoryStore(tmp_path / "memory.json")
    store.plus(10.0)
    assert store.minus(3.0) == 7.0
    assert store.snapshot().register == 7.0


def test_clear_register_resets_to_zero(tmp_path: Path) -> None:
    store = MemoryStore(tmp_path / "memory.json")
    store.plus(12.0)
    store.clear_register()
    assert store.snapshot().register == 0.0


def test_record_appends_history_entry(tmp_path: Path) -> None:
    store = MemoryStore(tmp_path / "memory.json")
    entry = store.record("add", 10.0, 2.0, 12.0)
    assert entry.operation == "add"
    assert entry.a == 10.0
    assert entry.b == 2.0
    assert entry.result == 12.0
    assert entry.at

    snap = store.snapshot()
    assert len(snap.history) == 1
    assert snap.history[0].result == 12.0


def test_clear_history_keeps_register(tmp_path: Path) -> None:
    store = MemoryStore(tmp_path / "memory.json")
    store.plus(4.0)
    store.record("multiply", 2.0, 3.0, 6.0)
    store.clear_history()
    snap = store.snapshot()
    assert snap.history == []
    assert snap.register == 4.0


def test_store_reloads_from_file(tmp_path: Path) -> None:
    path = tmp_path / "memory.json"
    first = MemoryStore(path)
    first.plus(8.0)
    first.record("subtract", 9.0, 1.0, 8.0)

    second = MemoryStore(path)
    snap = second.snapshot()
    assert snap.register == 8.0
    assert len(snap.history) == 1
    assert snap.history[0].operation == "subtract"
    assert snap.history[0].result == 8.0


def test_history_keeps_newest_100(tmp_path: Path) -> None:
    store = MemoryStore(tmp_path / "memory.json", max_history=100)
    for i in range(105):
        store.record("add", float(i), 1.0, float(i + 1))
    snap = store.snapshot()
    assert len(snap.history) == 100
    assert snap.history[0].a == 5.0
    assert snap.history[-1].a == 104.0


def test_record_unary_sqrt_persists_without_b(tmp_path: Path) -> None:
    path = tmp_path / "memory.json"
    first = MemoryStore(path)
    entry = first.record("sqrt", 9.0, None, 3.0)
    assert entry.b is None
    assert entry.result == 3.0

    second = MemoryStore(path)
    snap = second.snapshot()
    assert len(snap.history) == 1
    assert snap.history[0].operation == "sqrt"
    assert snap.history[0].a == 9.0
    assert snap.history[0].b is None
    assert snap.history[0].result == 3.0

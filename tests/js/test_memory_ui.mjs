import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { createContext, runInContext } from "node:vm";

const root = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const source = readFileSync(join(root, "src/calc_app/static/memory_ui.js"), "utf8");
const context = createContext({ globalThis: {} });
context.globalThis = context;
runInContext(source, context);
const { applyLoadedNumber, recallMemory } = context.CalcMemoryUi;

function freshState(overrides = {}) {
  return {
    current: "0",
    stored: 10,
    operator: "+",
    overwrite: false,
    error: "Division by zero",
    lastExpression: "10 + 0",
    busy: false,
    memoryRegister: 0,
    history: [],
    ...overrides,
  };
}

test("recallMemory waits for the server snapshot before showing the register", async () => {
  const state = freshState();
  let resolveSnapshot;
  const pending = new Promise((resolve) => {
    resolveSnapshot = resolve;
  });

  const recall = recallMemory(state, () => pending, (value) => String(value));
  assert.equal(state.current, "0");
  assert.equal(state.memoryRegister, 0);

  resolveSnapshot({ register: 42, history: [] });
  await recall;

  assert.equal(state.memoryRegister, 42);
  assert.equal(state.current, "42");
});

test("recallMemory clears a pending operation so equals does not reuse it", async () => {
  const state = freshState();
  await recallMemory(
    state,
    async () => ({ register: 7, history: [] }),
    (value) => String(value),
  );
  assert.equal(state.stored, null);
  assert.equal(state.operator, null);
  assert.equal(state.lastExpression, "MR");
});

test("applyLoadedNumber treats a history tap as a fresh starting value", () => {
  const state = freshState();
  applyLoadedNumber(state, "12", "");
  assert.equal(state.current, "12");
  assert.equal(state.stored, null);
  assert.equal(state.operator, null);
  assert.equal(state.overwrite, true);
  assert.equal(state.error, null);
});

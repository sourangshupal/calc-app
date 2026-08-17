(() => {
  const OPERATIONS = {
    "+": { path: "/add", symbol: "+" },
    "-": { path: "/subtract", symbol: "−" },
    "*": { path: "/multiply", symbol: "×" },
    "/": { path: "/divide", symbol: "÷" },
  };

  const HISTORY_SYMBOLS = {
    add: "+",
    subtract: "−",
    multiply: "×",
    divide: "÷",
    sqrt: "√",
  };

  const displayEl = document.getElementById("display");
  const expressionEl = document.getElementById("expression");
  const healthEl = document.getElementById("health");
  const healthLabelEl = document.getElementById("health-label");
  const padEl = document.getElementById("pad");
  const mFlagEl = document.getElementById("m-flag");
  const historyEl = document.getElementById("history");
  const historyEmptyEl = document.getElementById("history-empty");
  const historyClearEl = document.getElementById("history-clear");

  const state = {
    current: "0",
    stored: null,
    operator: null,
    overwrite: false,
    error: null,
    lastExpression: "",
    busy: false,
    memoryRegister: 0,
    history: [],
  };

  let memoryLoad = null;

  function formatNumber(value) {
    if (!Number.isFinite(value)) {
      return "Error";
    }
    return String(Number(value.toPrecision(12)));
  }

  function currentNumber() {
    return Number(state.current);
  }

  function extractError(body) {
    const detail = body && body.detail;
    if (typeof detail === "string" && detail) {
      return detail;
    }
    if (Array.isArray(detail) && detail.length) {
      const first = detail[0];
      if (typeof first === "string") {
        return first;
      }
      if (first && first.msg) {
        return first.msg;
      }
    }
    return "Invalid input";
  }

  function render() {
    if (state.error) {
      displayEl.textContent = state.error;
      displayEl.classList.add("is-error");
    } else {
      displayEl.textContent = state.current;
      displayEl.classList.remove("is-error");
    }

    if (state.operator && state.stored !== null) {
      const symbol = OPERATIONS[state.operator].symbol;
      const right = state.overwrite ? "" : ` ${state.current}`;
      expressionEl.textContent = `${formatNumber(state.stored)} ${symbol}${right}`;
    } else if (state.lastExpression) {
      expressionEl.textContent = state.lastExpression;
    } else {
      expressionEl.textContent = "\u00a0";
    }

    padEl.querySelectorAll("[data-op]").forEach((button) => {
      button.classList.toggle("is-pending", button.dataset.op === state.operator);
    });

    mFlagEl.hidden = state.memoryRegister === 0;
    renderHistory();
  }

  function renderHistory() {
    historyEl.replaceChildren();
    const entries = [...state.history].reverse();
    historyEmptyEl.hidden = entries.length > 0;
    for (const entry of entries) {
      const symbol = HISTORY_SYMBOLS[entry.operation] || entry.operation;
      const item = document.createElement("li");
      const button = document.createElement("button");
      button.type = "button";
      button.className = "tape-item";
      button.dataset.result = String(entry.result);
      const expr = document.createElement("p");
      expr.className = "tape-expr";
      if (entry.operation === "sqrt") {
        expr.textContent = `√${formatNumber(entry.a)}`;
      } else {
        expr.textContent = `${formatNumber(entry.a)} ${symbol} ${formatNumber(entry.b)}`;
      }
      const result = document.createElement("p");
      result.className = "tape-result";
      result.textContent = formatNumber(entry.result);
      button.append(expr, result);
      item.appendChild(button);
      historyEl.appendChild(item);
    }
  }

  function clearAll() {
    state.current = "0";
    state.stored = null;
    state.operator = null;
    state.overwrite = false;
    state.error = null;
    state.lastExpression = "";
    render();
  }

  function beginFreshEntry() {
    state.error = null;
    state.overwrite = false;
    state.lastExpression = "";
  }

  function inputDigit(digit) {
    if (state.busy) {
      return;
    }
    if (state.error || state.overwrite) {
      state.current = digit;
      beginFreshEntry();
      render();
      return;
    }
    if (state.current.replace("-", "").replace(".", "").length >= 16) {
      return;
    }
    state.current = state.current === "0" ? digit : `${state.current}${digit}`;
    render();
  }

  function inputDecimal() {
    if (state.busy) {
      return;
    }
    if (state.error || state.overwrite) {
      state.current = "0.";
      beginFreshEntry();
      render();
      return;
    }
    if (!state.current.includes(".")) {
      state.current = `${state.current}.`;
      render();
    }
  }

  function backspace() {
    if (state.busy) {
      return;
    }
    if (state.error) {
      clearAll();
      return;
    }
    if (state.overwrite) {
      return;
    }
    if (state.current.length <= 1 || (state.current.length === 2 && state.current.startsWith("-"))) {
      state.current = "0";
    } else {
      state.current = state.current.slice(0, -1);
    }
    render();
  }

  function setOperator(operator) {
    if (state.busy || !OPERATIONS[operator]) {
      return;
    }
    if (state.error) {
      return;
    }
    if (state.stored !== null && state.operator && !state.overwrite) {
      evaluate().then((ok) => {
        if (ok) {
          state.operator = operator;
          state.overwrite = true;
          state.lastExpression = "";
          render();
        }
      });
      return;
    }
    state.stored = currentNumber();
    state.operator = operator;
    state.overwrite = true;
    state.lastExpression = "";
    render();
  }

  async function evaluate() {
    if (state.busy || state.error || !state.operator || state.stored === null) {
      return false;
    }

    const meta = OPERATIONS[state.operator];
    const a = state.stored;
    const b = currentNumber();
    const pending = `${formatNumber(a)} ${meta.symbol} ${formatNumber(b)}`;

    state.busy = true;
    try {
      const response = await fetch(meta.path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ a, b }),
      });
      const body = await response.json();
      if (response.ok) {
        state.current = formatNumber(body.result);
        state.stored = body.result;
        state.operator = null;
        state.overwrite = true;
        state.error = null;
        state.lastExpression = `${pending} =`;
        await refreshMemory();
        return true;
      }
      state.error = extractError(body);
      state.lastExpression = pending;
      return false;
    } catch {
      state.error = "Network error";
      state.lastExpression = pending;
      return false;
    } finally {
      state.busy = false;
      render();
    }
  }

  async function applySqrt() {
    if (state.busy || state.error) {
      return;
    }

    const a = currentNumber();
    const pending = `√${formatNumber(a)}`;

    state.busy = true;
    try {
      const response = await fetch("/sqrt", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ a }),
      });
      const body = await response.json();
      if (response.ok) {
        state.current = formatNumber(body.result);
        state.overwrite = true;
        state.error = null;
        state.lastExpression = `${pending} =`;
        await refreshMemory();
        return;
      }
      state.error = extractError(body);
      state.lastExpression = pending;
    } catch {
      state.error = "Network error";
      state.lastExpression = pending;
    } finally {
      state.busy = false;
      render();
    }
  }

  async function fetchMemorySnapshot() {
    const response = await fetch("/memory");
    if (!response.ok) {
      throw new Error("memory");
    }
    return response.json();
  }

  function loadMemorySnapshot() {
    if (!memoryLoad) {
      memoryLoad = fetchMemorySnapshot().finally(() => {
        memoryLoad = null;
      });
    }
    return memoryLoad;
  }

  async function refreshMemory() {
    try {
      applyMemory(await loadMemorySnapshot());
    } catch {
      // Keep the last known tape if the memory endpoint is unreachable.
    }
  }

  function applyMemory(body) {
    state.memoryRegister = Number(body.register) || 0;
    state.history = Array.isArray(body.history) ? body.history : [];
    render();
  }

  async function memoryRequest(url, options) {
    if (state.busy) {
      return;
    }
    state.busy = true;
    try {
      const response = await fetch(url, options);
      const body = await response.json();
      if (response.ok) {
        applyMemory(body);
        return;
      }
      state.error = extractError(body);
      render();
    } catch {
      state.error = "Network error";
      render();
    } finally {
      state.busy = false;
    }
  }

  function memoryPlus() {
    if (state.error) {
      return;
    }
    memoryRequest("/memory/plus", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ value: currentNumber() }),
    });
  }

  function memoryMinus() {
    if (state.error) {
      return;
    }
    memoryRequest("/memory/minus", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ value: currentNumber() }),
    });
  }

  function memoryClear() {
    memoryRequest("/memory/register", { method: "DELETE" });
  }

  async function memoryRecall() {
    if (state.busy) {
      return;
    }
    state.busy = true;
    try {
      await CalcMemoryUi.recallMemory(state, loadMemorySnapshot, formatNumber);
    } catch {
      state.error = "Network error";
    } finally {
      state.busy = false;
      render();
    }
  }

  function loadHistoryResult(value) {
    if (state.busy) {
      return;
    }
    const number = Number(value);
    if (!Number.isFinite(number)) {
      return;
    }
    CalcMemoryUi.applyLoadedNumber(state, formatNumber(number), "");
    render();
  }

  function clearHistory() {
    memoryRequest("/memory/history", { method: "DELETE" });
  }

  async function checkHealth() {
    try {
      const response = await fetch("/health");
      const body = await response.json();
      const ok = response.ok && body.status === "ok";
      healthEl.dataset.status = ok ? "ok" : "down";
      healthLabelEl.textContent = ok ? "API online" : "API down";
    } catch {
      healthEl.dataset.status = "down";
      healthLabelEl.textContent = "API down";
    }
  }

  padEl.addEventListener("click", (event) => {
    const button = event.target.closest("button");
    if (!button) {
      return;
    }
    if (button.dataset.digit) {
      inputDigit(button.dataset.digit);
      return;
    }
    if (button.dataset.op) {
      setOperator(button.dataset.op);
      return;
    }
    const action = button.dataset.action;
    if (action === "clear") {
      clearAll();
    } else if (action === "backspace") {
      backspace();
    } else if (action === "decimal") {
      inputDecimal();
    } else if (action === "equals") {
      evaluate();
    } else if (action === "sqrt") {
      applySqrt();
    } else if (action === "memory-plus") {
      memoryPlus();
    } else if (action === "memory-minus") {
      memoryMinus();
    } else if (action === "memory-clear") {
      memoryClear();
    } else if (action === "memory-recall") {
      memoryRecall();
    }
  });

  historyEl.addEventListener("click", (event) => {
    const button = event.target.closest(".tape-item");
    if (!button) {
      return;
    }
    loadHistoryResult(button.dataset.result);
  });

  historyClearEl.addEventListener("click", () => {
    clearHistory();
  });

  window.addEventListener("keydown", (event) => {
    if (event.metaKey || event.ctrlKey || event.altKey) {
      return;
    }
    const key = event.key;
    if (/^[0-9]$/.test(key)) {
      event.preventDefault();
      inputDigit(key);
      return;
    }
    if (key === ".") {
      event.preventDefault();
      inputDecimal();
      return;
    }
    if (key === "+" || key === "-" || key === "*" || key === "/") {
      event.preventDefault();
      setOperator(key);
      return;
    }
    if (key === "Enter" || key === "=") {
      event.preventDefault();
      evaluate();
      return;
    }
    if (key === "Escape" || key === "c" || key === "C") {
      event.preventDefault();
      clearAll();
      return;
    }
    if (key === "Backspace") {
      event.preventDefault();
      backspace();
      return;
    }
    if (key === "r" || key === "R") {
      event.preventDefault();
      applySqrt();
    }
  });

  render();
  checkHealth();
  refreshMemory();
  setInterval(checkHealth, 15000);
})();

(() => {
  const root = typeof globalThis !== "undefined" ? globalThis : window;

  function applyLoadedNumber(state, formattedValue, lastExpression) {
    state.current = formattedValue;
    state.stored = null;
    state.operator = null;
    state.overwrite = true;
    state.error = null;
    state.lastExpression = lastExpression;
  }

  async function recallMemory(state, loadSnapshot, formatNumber) {
    const snapshot = await loadSnapshot();
    state.memoryRegister = Number(snapshot.register) || 0;
    if (Array.isArray(snapshot.history)) {
      state.history = snapshot.history;
    }
    applyLoadedNumber(state, formatNumber(state.memoryRegister), "MR");
  }

  root.CalcMemoryUi = { applyLoadedNumber, recallMemory };
})();

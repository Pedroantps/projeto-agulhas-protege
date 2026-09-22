import '@testing-library/jest-dom/vitest';
import axe, { type ElementContext, type RunOptions } from 'axe-core';

class MockResizeObserver {
  observe(): void {}
  unobserve(): void {}
  disconnect(): void {}
}

if (typeof window !== 'undefined' && !window.ResizeObserver) {
  window.ResizeObserver = MockResizeObserver;
}

if (!globalThis.ResizeObserver) {
  globalThis.ResizeObserver = MockResizeObserver;
}

export const defaultAxeOptions: RunOptions = {
  rules: {
    'color-contrast': { enabled: false },
    label: { enabled: true },
    'aria-required-attr': { enabled: true },
  },
};

export async function checkA11y(
  context: ElementContext,
  options: RunOptions = defaultAxeOptions,
) {
  return axe.run(context, options);
}

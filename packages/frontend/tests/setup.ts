import '@testing-library/jest-dom';
import { afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';

// Polyfill for Radix UI pointer capture methods (missing in JSDOM)
if (typeof Element.prototype.hasPointerCapture === 'undefined') {
  Element.prototype.hasPointerCapture = function () {
    return false;
  };
}

if (typeof Element.prototype.setPointerCapture === 'undefined') {
  Element.prototype.setPointerCapture = function () {
    // No-op
  };
}

if (typeof Element.prototype.releasePointerCapture === 'undefined') {
  Element.prototype.releasePointerCapture = function () {
    // No-op
  };
}

// Polyfill for scrollIntoView (missing in JSDOM)
if (typeof Element.prototype.scrollIntoView === 'undefined') {
  Element.prototype.scrollIntoView = function () {
    // No-op
  };
}

// Cleanup after each test
afterEach(() => {
  cleanup();
});

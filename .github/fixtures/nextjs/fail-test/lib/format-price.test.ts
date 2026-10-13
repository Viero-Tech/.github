import { describe, expect, it } from 'vitest';
import { formatPrice } from './format-price';

describe('formatPrice', () => {
  it('should format cents as a two-decimal amount', () => {
    expect(formatPrice(1250)).toBe('12.5 USD'); // Defect: wrong expectation
  });
});

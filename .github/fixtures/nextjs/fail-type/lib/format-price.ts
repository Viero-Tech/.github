export function formatPrice(cents: number): string {
  return `${(cents / 100).toFixed(2)} USD`;
}

// Defect: a type error. ESLint accepts it; tsc rejects it.
export const currency: number = 'USD';

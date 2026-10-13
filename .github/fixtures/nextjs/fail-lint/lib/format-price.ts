export function formatPrice(cents: number): string {
  return `${(cents / 100).toFixed(2)} USD`;
}

// Defect: an unused variable. tsc accepts it; ESLint rejects it.
const unusedRate = 3;

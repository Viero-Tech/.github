import { isInStock } from '../src/widget';

describe('isInStock', () => {
  it('should be true when stock is positive', () => {
    expect(isInStock({ id: 1, name: 'bolt', stock: 3 })).toBe(true);
  });

  it('should be false when stock is zero', () => {
    expect(isInStock({ id: 2, name: 'nut', stock: 0 })).toBe(true); // Defect: wrong expectation
  });
});

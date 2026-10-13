import { isInStock } from '../src/widget';

describe('widget e2e', () => {
  it('should report stock for a widget', () => {
    expect(isInStock({ id: 3, name: 'washer', stock: 1 })).toBe(true);
  });
});

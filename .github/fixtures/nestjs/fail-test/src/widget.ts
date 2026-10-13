import type { Widget } from '@prisma/client';

// Type-aware lint and the typecheck both resolve Widget from the generated
// client, so this file only passes when the client is generated first.
export function isInStock(widget: Widget): boolean {
  return widget.stock > 0;
}

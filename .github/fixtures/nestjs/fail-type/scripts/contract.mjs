// Stands in for a contract check: fails when the committed contract file
// does not list the exported function.
import { readFileSync } from 'node:fs';

const contract = JSON.parse(readFileSync(new URL('../contract.json', import.meta.url), 'utf8'));
if (!contract.exports.includes('isInStock')) {
  console.error('contract.json does not list isInStock');
  process.exit(1);
}
console.log('contract matches');

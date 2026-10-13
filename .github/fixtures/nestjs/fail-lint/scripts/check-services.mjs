// Stands in for a migration script: proves that the service containers the
// caller asked for are reachable through the URLs the workflow exports.
import net from 'node:net';

function reach(name, rawUrl) {
  if (!rawUrl) {
    console.log(`${name} not requested`);
    return Promise.resolve();
  }
  const url = new URL(rawUrl);
  return new Promise((resolve, reject) => {
    const socket = net.connect(Number(url.port), url.hostname, () => {
      console.log(`${name} reachable on port ${url.port}`);
      socket.end();
      resolve();
    });
    socket.on('error', reject);
  });
}

await reach('database', process.env.DATABASE_URL);
await reach('redis', process.env.REDIS_URL);

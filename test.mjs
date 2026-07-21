import fs from 'node:fs';
import assert from 'node:assert/strict';
const pkg=JSON.parse(fs.readFileSync('package.json','utf8'));
assert.equal(pkg.scripts.start,'node server.mjs');
assert.ok(fs.readFileSync('index.html','utf8').includes('/app.js'));
assert.ok(fs.readFileSync('server.mjs','utf8').includes('const publicDir = __dirname;'));
for (const f of ['index.html','app.js','styles.css','manifest.webmanifest','sw.js','icon.svg']) {
  assert.ok(fs.existsSync(f), `Missing ${f}`);
}
console.log('FLAT tests passed');

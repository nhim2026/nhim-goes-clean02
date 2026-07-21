import fs from 'node:fs';
const required=[
  'package.json','server.mjs','index.html','app.js','styles.css',
  'manifest.webmanifest','sw.js','icon.svg','Dockerfile'
];
for (const f of required) {
  if (!fs.existsSync(f)) throw new Error(`Missing ${f}`);
}
console.log('FLAT build check passed');

/** Verify that shipped aggregate chunks equal the original public JSON exactly. */
import { createHash } from 'node:crypto';
import { readFile, readdir } from 'node:fs/promises';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { resolve } from 'node:path';
import assert from 'node:assert/strict';
const root = fileURLToPath(new URL('../', import.meta.url));
const assets = await readdir(resolve(root, 'dist/assets'));
for (const name of ['capacity_comparison_v2', 'robustness_v1']) {
  const original = await readFile(resolve(root, `../artifacts/${name}.json`));
  const chunk = assets.filter(file => file.startsWith(`${name}-`) && file.endsWith('.js'));
  assert.equal(chunk.length, 1, `Exactly one ${name} chunk`);
  const shipped = await import(pathToFileURL(resolve(root, 'dist/assets', chunk[0])).href);
  assert.deepEqual(shipped.default, JSON.parse(original), `${name}: byte-equivalent decoded JSON`);
}
const robustness = JSON.parse(await readFile(resolve(root, '../artifacts/robustness_v1.json')));
const comparison = await readFile(resolve(root, '../artifacts/capacity_comparison_v2.json'));
assert.equal(createHash('sha256').update(comparison).digest('hex'), robustness.public_comparison.sha256);
const allowed = /^(index\.html|assets\/[\w.-]+\.(js|css))$/;
async function inspect(directory, prefix = '') {
  for (const file of await readdir(directory, { withFileTypes: true })) {
    const path = `${prefix}${file.name}`;
    if (file.isDirectory()) await inspect(resolve(directory, file.name), `${path}/`);
    else {
      assert.match(path, allowed, `Unapproved build file: ${path}`);
      const text = await readFile(resolve(directory, file.name), 'utf8');
      assert.doesNotMatch(text, /data\/(raw|processed)|BEGIN (?:OPENSSH |RSA |EC )?PRIVATE KEY|msno|\.joblib|\.pickle|\/home\/fjrc94/);
    }
  }
}
await inspect(resolve(root, 'dist'));
console.log('PASS: both shipped JSON chunks equal source; comparison SHA-256 verified; dist allowlist/privacy scan passed.');

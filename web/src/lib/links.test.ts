import { describe, expect, it } from 'vitest';
import { existsSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { doc, repo } from './links';

describe('repository documentation links', () => {
  it('uses integrated main documents with existing destinations', () => {
    for (const path of ['docs/results.md', 'docs/robustness.md', 'docs/limitations.md',
      'docs/data_attribution.md', 'docs/methodology.md', 'web/README.md']) {
      expect(doc(path)).toBe(`${repo}/blob/main/${path}`);
      expect(existsSync(resolve('..', path))).toBe(true);
    }
  });
  it('preserves the repository footer and technical evidence links', () => {
    expect(repo).toBe('https://github.com/FranRguezCer/retention-lab');
    for (const source of ['src/App.tsx', 'src/components/TechnicalEvidence.tsx']) {
      const text = readFileSync(source, 'utf8');
      for (const match of text.matchAll(/doc\('([^']+)'\)/g)) {
        expect(existsSync(resolve('..', match[1]))).toBe(true);
        expect(doc(match[1])).toContain('/blob/main/');
      }
    }
  });
});

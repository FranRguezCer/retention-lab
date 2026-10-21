import { describe, expect, it } from 'vitest';
import { developmentRef, doc, repo, stableDocuments } from './links';

describe('repository documentation links', () => {
  it('uses main only for the documents verified equivalent at this release', () => {
    for (const path of stableDocuments) expect(doc(path)).toBe(`${repo}/blob/main/${path}`);
  });
  it('keeps the current methodology and unmerged web guide on the development branch', () => {
    for (const path of ['docs/methodology.md', 'web/README.md']) {
      expect(doc(path)).toBe(`${repo}/blob/${developmentRef}/${path}`);
    }
  });
});

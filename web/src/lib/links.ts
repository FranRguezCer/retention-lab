/** Change this one fallback after the interactive demo is merged into main. */
export const developmentRef = 'feat/retention-interactive-demo';
export const repo = 'https://github.com/FranRguezCer/retention-lab';
// Verified byte-equivalent to origin/main at the start of this iteration.
export const stableDocuments = [
  'docs/results.md', 'docs/robustness.md', 'docs/limitations.md',
  'docs/data_attribution.md',
] as const;
export const doc = (path: string): string => {
  const ref = stableDocuments.some(document => document === path) ? 'main' : developmentRef;
  return `${repo}/blob/${ref}/${path}`;
};

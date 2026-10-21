/** The UI consumes published aggregates only; no ranking or prediction is computed. */
export const strategies = ['random_expected', 'business', 'logistic', 'hgb'] as const;
export type Strategy = typeof strategies[number];
export const empirical = ['business', 'logistic', 'hgb'] as const;
export type Empirical = typeof empirical[number];
export const pairs = [
  ['hgb', 'business'], ['hgb', 'logistic'], ['logistic', 'business'],
] as const;
export const labels: Record<Strategy, string> = {
  random_expected: 'Random expected', business: 'Business Rule',
  logistic: 'Logistic Regression', hgb: 'HistGradientBoosting',
};
export const colors: Record<Strategy, string> = {
  random_expected: '#66717a', business: '#2465ad', logistic: '#16704c', hgb: '#b44b18',
};
export const dashes: Record<Strategy, string> = {
  random_expected: '5 5', business: '10 3', logistic: '2 3', hgb: '',
};
export interface Metrics {
  capacity: number; captured: number; k: number; n: number; positives: number;
  recall: number; precision: number | null; lift: number | null;
}
export type CapacityRow = Record<Strategy, Metrics> & { requested_percent: number } & Record<`${string}_recall_pp`, number>;
interface Interval { estimate: number; interval_95: [number, number] }
export interface BootstrapRow {
  requested_percent: number; k: number;
  recall: Record<Empirical, Interval>;
  differences_pp: Record<string, Interval>;
}
export interface Data {
  n: number; positives: number; prevalence: number; cutoff: string;
  curve: CapacityRow[];
  bootstrap: { capacities: BootstrapRow[]; replicates: number; estimand: string; interval: string };
}
function check(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(`Invalid public aggregate: ${message}`);
}
function object(value: unknown): Record<string, unknown> {
  check(value !== null && typeof value === 'object' && !Array.isArray(value), 'expected object');
  return value as Record<string, unknown>;
}
function numeric(value: unknown, min = 0, max = Infinity): number {
  check(typeof value === 'number' && Number.isFinite(value) && value >= min && value <= max, 'numeric range');
  return value;
}
function integer(value: unknown, min = 0, max = Infinity): number {
  const n = numeric(value, min, max);
  check(Number.isInteger(n), 'integer required');
  return n;
}
function close(actual: unknown, expected: number): void {
  const n = numeric(actual, -Infinity);
  check(Math.abs(n - expected) <= 1e-9 * Math.max(1, Math.abs(expected)), 'inconsistent metric');
}
function interval(value: unknown, estimate: number, min: number, max: number): void {
  const v = object(value);
  close(v.estimate, estimate);
  check(Array.isArray(v.interval_95) && v.interval_95.length === 2, 'interval missing');
  const [lo, hi] = v.interval_95.map(x => numeric(x, min, max));
  check(lo <= hi, 'reversed interval');
}
/** Fail closed before rendering if source versions, populations or metrics disagree. */
export function validateData(comparison: unknown, robustness: unknown): Data {
  const c = object(comparison), r = object(robustness);
  check(c.version === 2 && r.version === 1 && c.selected_model === 'hgb', 'unsupported artifact version/model');
  const n = integer(c.n, 1), positives = integer(c.positives, 1, n);
  close(c.prevalence, positives / n);
  check(typeof c.cutoff === 'string' && /^\d{8}$/.test(c.cutoff), 'cutoff');
  check(r.n === n && r.positives === positives && r.cutoff === c.cutoff, 'cohort mismatch');
  check(Array.isArray(c.curve) && c.curve.length === 101, '101 capacities required');
  for (const [p, entry] of c.curve.entries()) {
    const row = object(entry);
    check(row.requested_percent === p, 'capacities must be unique ordered integers 0–100');
    const k = Math.floor(n * p / 100);
    for (const key of strategies) {
      const m = object(row[key]);
      check(m.n === n && m.positives === positives && m.k === k, 'population or K mismatch');
      close(m.capacity, k / n);
      // A selected group cannot exclude more positives than the unselected group holds.
      const captured = numeric(m.captured, Math.max(0, k + positives - n), Math.min(k, positives));
      if (key !== 'random_expected') integer(captured);
      else close(captured, positives * k / n);
      numeric(m.recall, 0, 1);
      close(m.recall, captured / positives);
      if (k === 0) check(m.precision === null && m.lift === null, 'K=0 requires null precision/lift');
      else {
        numeric(m.precision, 0, 1);
        close(m.precision, captured / k);
        close(m.lift, captured / k / (positives / n));
      }
    }
    for (const [a, b] of [...pairs, ['hgb', 'random_expected'], ['logistic', 'random_expected']] as const) {
      close(row[`${a}_minus_${b}_recall_pp`],
        (numeric(object(row[a]).recall) - numeric(object(row[b]).recall)) * 100);
    }
  }
  const bootstrap = object(r.bootstrap);
  integer(bootstrap.replicates, 1);
  check(typeof bootstrap.estimand === 'string' && typeof bootstrap.interval === 'string', 'bootstrap metadata');
  check(Array.isArray(bootstrap.capacities) && bootstrap.capacities.length === 3, 'bootstrap capacities');
  for (const [i, entry] of bootstrap.capacities.entries()) {
    const b = object(entry), p = [5, 10, 20][i];
    check(b.requested_percent === p && b.k === Math.floor(n * p / 100), 'bootstrap capacity mismatch');
    const row = object(c.curve[p]);
    for (const key of empirical) interval(object(b.recall)[key], numeric(object(row[key]).recall), 0, 1);
    for (const [a, key] of pairs) interval(object(b.differences_pp)[`${a}_minus_${key}`], numeric(row[`${a}_minus_${key}_recall_pp`], -100, 100), -100, 100);
  }
  return { n, positives, prevalence: positives / n, cutoff: c.cutoff,
    curve: c.curve as CapacityRow[], bootstrap: bootstrap as unknown as Data['bootstrap'] };
}
/** Exact lookup only: never interpolate between published capacity records. */
export function capacityAt(data: Data, percent: number): CapacityRow {
  check(Number.isInteger(percent) && percent >= 0 && percent <= 100, 'unavailable capacity');
  const row = data.curve.find(r => r.requested_percent === percent);
  check(row, 'missing capacity');
  return row;
}
export function difference(row: CapacityRow, a: Empirical, b: Empirical) {
  return { captures: row[a].captured - row[b].captured, pp: (row[a].recall - row[b].recall) * 100 };
}
export const percent = (n: number | null, digits = 2): string =>
  n === null ? 'N/A' : `${(n * 100).toFixed(digits)}%`;
export const count = (n: number, expected = false): string =>
  new Intl.NumberFormat('en-US', { maximumFractionDigits: expected ? 1 : 0 }).format(n) + (expected ? ' expected' : '');
export const lift = (n: number | null): string => n === null ? 'N/A' : `${n.toFixed(2)}×`;
export const signed = (n: number, digits = 2): string => `${n >= 0 ? '+' : '−'}${Math.abs(n).toFixed(digits)}`;

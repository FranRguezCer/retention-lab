import { describe, expect, it } from 'vitest';
import comparison from '../../../artifacts/capacity_comparison_v2.json';
import robustness from '../../../artifacts/robustness_v1.json';
import { validateData, capacityAt, difference, percent, count, lift } from './data';

const load = () => validateData(comparison, robustness);
describe('published aggregate contract', () => {
  it('loads all and only the 101 published records', () => {
    const data = load();
    expect(data.curve).toEqual(comparison.curve);
    for (const p of [0, 5, 10, 20, 100]) {
      const row = capacityAt(data, p);
      expect(row).toEqual(comparison.curve[p]);
      for (const key of ['random_expected', 'business', 'logistic', 'hgb'] as const) {
        const m = row[key];
        expect(m.k).toBe(Math.floor(data.n * p / 100));
        expect(m.recall).toBeCloseTo(m.captured / data.positives, 12);
        expect(m.precision).toEqual(m.k === 0 ? null : m.captured / m.k);
        if (m.k) expect(m.lift).toBeCloseTo(m.precision! / data.prevalence, 12);
      }
    }
  });
  it('refuses interpolation or an unavailable capacity', () => {
    for (const p of [-1, 1.5, 101, NaN]) expect(() => capacityAt(load(), p)).toThrow();
  });
  it('preserves null and fractional expected counts', () => {
    const data = load();
    expect(capacityAt(data, 0).hgb.precision).toBeNull();
    expect(capacityAt(data, 0).hgb.lift).toBeNull();
    expect(Number.isInteger(capacityAt(data, 10).random_expected.captured)).toBe(false);
    expect(percent(null)).toBe('N/A');
    expect(lift(null)).toBe('N/A');
    expect(count(952.6945538526619, true)).toBe('952.7 expected');
  });
  it('calculates differences before rounding', () => {
    const row = capacityAt(load(), 10);
    expect(difference(row, 'hgb', 'business')).toEqual({ captures: 641, pp: row.hgb_minus_business_recall_pp });
    expect(difference(row, 'hgb', 'logistic').captures).toBe(123);
    expect(difference(row, 'logistic', 'business').captures).toBe(518);
  });
  it('keeps bootstrap restricted to published capacities', () => {
    expect(load().bootstrap.capacities.map(r => r.requested_percent)).toEqual([5, 10, 20]);
  });
  const mutations: [string, (c: any, r: any) => void][] = [
    ['missing field', c => { delete c.curve[10].hgb.recall; }],
    ['missing strategy', c => { delete c.curve[10].logistic; }],
    ['duplicate capacity', c => { c.curve[11].requested_percent = 10; }],
    ['wrong K', c => { c.curve[10].business.k++; }],
    ['wrong population', c => { c.curve[10].business.n++; }],
    ['out of range', c => { c.curve[10].hgb.recall = 1.1; }],
    ['nonnumeric', c => { c.curve[10].hgb.captured = '5968'; }],
    ['unexpected null', c => { c.curve[10].hgb.precision = null; }],
    ['zero substituted for null', c => { c.curve[0].hgb.lift = 0; }],
    ['fractional empirical count', c => { c.curve[10].hgb.captured += 0.5; }],
    ['internally consistent but impossible full-population count', c => {
      const row = c.curve[100];
      for (const key of ['business', 'logistic', 'hgb']) {
        const m = row[key];
        m.captured--;
        m.recall = m.captured / m.positives;
        m.precision = m.captured / m.k;
        m.lift = m.precision / c.prevalence;
      }
      for (const [a, b] of [['hgb', 'business'], ['hgb', 'logistic'], ['logistic', 'business'], ['hgb', 'random_expected'], ['logistic', 'random_expected']]) {
        row[`${a}_minus_${b}_recall_pp`] = (row[a].recall - row[b].recall) * 100;
      }
    }],
    ['wrong difference', c => { c.curve[10].hgb_minus_business_recall_pp = 0; }],
    ['wrong random expectation', c => { c.curve[10].random_expected.captured++; }],
    ['nonfinite', c => { c.curve[10].hgb.lift = Infinity; }],
    ['mismatched bootstrap', (_c, r) => { r.n++; }],
    ['unsupported interval', (_c, r) => { r.bootstrap.capacities[0].requested_percent = 6; }],
    ['reversed interval', (_c, r) => { r.bootstrap.capacities[0].recall.hgb.interval_95 = [0.9, 0.1]; }],
    ['missing interval', (_c, r) => { delete r.bootstrap.capacities[0].recall.logistic; }],
    ['wrong bootstrap estimate', (_c, r) => { r.bootstrap.capacities[0].recall.hgb.estimate = 0; }],
  ];
  it.each(mutations)('rejects %s', (_name, mutate) => {
    const c = structuredClone(comparison), r = structuredClone(robustness);
    mutate(c, r);
    expect(() => validateData(c, r)).toThrow();
  });
});

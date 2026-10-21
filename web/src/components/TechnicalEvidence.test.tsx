import { cleanup, render, screen, within } from '@testing-library/react';
import { afterEach, describe, expect, it } from 'vitest';
import comparison from '../../../artifacts/capacity_comparison_v2.json';
import robustness from '../../../artifacts/robustness_v1.json';
import { count, signed, validateData } from '../lib/data';
import { TechnicalEvidence } from './TechnicalEvidence';

const data = validateData(comparison, robustness);
afterEach(cleanup);

describe('progressive technical evidence', () => {
  it('summarizes robustness and renders every published paired comparison without copied metrics', () => {
    render(<TechnicalEvidence data={data} capacity={10} />);
    expect(screen.getByRole('heading', { name: 'Robustness at a glance' })).toBeTruthy();
    expect(screen.getByText(count(data.bootstrap.replicates))).toBeTruthy();
    expect(screen.getByRole('heading', { name: 'Methodology & limitations' })).toBeTruthy();
    for (const row of data.bootstrap.capacities) {
      const card = screen.getByTestId(`comparison-interval-${row.requested_percent}`);
      const interval = row.differences_pp.hgb_minus_logistic;
      expect(within(card).getByText(`${signed(interval.estimate)} pp`)).toBeTruthy();
      expect(card.textContent).toContain(interval.interval_95.map(v => v.toFixed(2)).join(' to '));
      expect(card.getAttribute('data-selected')).toBe(String(row.requested_percent === 10));
    }
    const detail = screen.getByTestId('bootstrap-intervals');
    expect(detail.textContent).toContain('HGB − Rule');
    expect(detail.textContent).toContain('HGB − LR');
    expect(detail.textContent).toContain('LR − Rule');
  });

  it.each([5, 10, 20])('highlights only the exact %i percent checkpoint and retains all source intervals', capacity => {
    render(<TechnicalEvidence data={data} capacity={capacity} />);
    const row = data.bootstrap.capacities.find(entry => entry.requested_percent === capacity)!;
    expect(document.querySelectorAll('[data-selected="true"]')).toHaveLength(1);
    expect(screen.getByTestId(`comparison-interval-${capacity}`).getAttribute('data-selected')).toBe('true');
    const detail = screen.getByTestId('bootstrap-intervals');
    for (const value of Object.values(row.differences_pp)) {
      expect(detail.textContent).toContain(value.interval_95.map(v => v.toFixed(2)).join(' – '));
    }
  });

  it.each([0, 11, 100])('does not invent an interval for %i percent', capacity => {
    render(<TechnicalEvidence data={data} capacity={capacity} />);
    expect(screen.queryByTestId('bootstrap-intervals')).toBeNull();
    expect(screen.getByText('Uncertainty intervals are available at 5%, 10% and 20% outreach capacity.')).toBeTruthy();
    expect(document.querySelectorAll('[data-selected="true"]')).toHaveLength(0);
    expect(screen.getAllByTestId(/comparison-interval-/)).toHaveLength(3);
  });
});

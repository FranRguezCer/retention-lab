import { cleanup, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import comparison from '../../../artifacts/capacity_comparison_v2.json';
import robustness from '../../../artifacts/robustness_v1.json';
import { count, labels, percent, strategies, validateData } from '../lib/data';
import { CapacityChart, CapacityTooltip } from './CapacityChart';

vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: any) => <div>{children}</div>,
  LineChart: ({ children }: any) => <div>{children}</div>,
  Line: ({ dataKey, type }: any) => <span data-testid={`curve-${dataKey}`}>{type}</span>,
  XAxis: () => null, YAxis: () => null, CartesianGrid: () => null, Tooltip: () => null,
  ReferenceLine: ({ x }: any) => <span data-testid="capacity-marker">{x}</span>,
  ReferenceDot: () => null,
}));
afterEach(cleanup);
const data = validateData(comparison, robustness);

describe('capacity chart presentation', () => {
  it('distinguishes a hovered record from selected capacity without substituting its metrics', () => {
    const hovered = data.curve[51];
    render(<CapacityTooltip hovered={hovered} selected={data.curve[10]} />);
    expect(screen.getByText('Hovered capacity: 51%')).toBeTruthy();
    expect(screen.getByText('Selected capacity: 10%')).toBeTruthy();
    expect(screen.getByText(`${count(hovered.hgb.k)} of ${count(hovered.hgb.n)} subscribers selected`)).toBeTruthy();
    for (const key of strategies) {
      const item = screen.getByTestId(`tooltip-${key}`);
      expect(item.textContent).toBe(`${labels[key]}${percent(hovered[key].recall)}`);
    }
  });
  it.each([0, 10, 100])('preserves the exact selected record and four curves at %i%%', p => {
    const row = data.curve[p];
    render(<CapacityChart rows={data.curve} row={row} />);
    expect(screen.getByTestId('chart-selection').textContent).toContain(`Selected capacity: ${p}% outreach capacity`);
    expect(screen.getByTestId('chart-selection').textContent).toContain(`${count(row.hgb.k)} of ${count(row.hgb.n)}`);
    expect(screen.getByTestId('capacity-marker').textContent).toBe(String(row.hgb.capacity * 100));
    for (const key of strategies) expect(screen.getByTestId(`curve-${key}`).textContent).toBe('linear');
  });
  it.each([0, 10, 100])('shows exact sampled recall at %i%% when hover and selection match', p => {
    const row = data.curve[p];
    render(<CapacityTooltip hovered={row} selected={row} />);
    expect(screen.getByText(`Hovered capacity: ${p}%`)).toBeTruthy();
    expect(screen.getByText(`Selected capacity: ${p}%`)).toBeTruthy();
    for (const key of strategies) {
      expect(screen.getByTestId(`tooltip-${key}`).textContent).toBe(`${labels[key]}${percent(row[key].recall)}`);
    }
  });
});

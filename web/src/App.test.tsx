import { cleanup, fireEvent, render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import comparison from '../../artifacts/capacity_comparison_v2.json';
import robustness from '../../artifacts/robustness_v1.json';
import App from './App';
import { validateData, count, percent, lift } from './lib/data';

vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: any) => <div>{children}</div>,
  LineChart: ({ children }: any) => <div>{children}</div>,
  Line: () => null, XAxis: () => null, YAxis: () => null,
  CartesianGrid: () => null, Tooltip: () => null, ReferenceLine: () => null, ReferenceDot: () => null,
}));
afterEach(cleanup);
const data = validateData(comparison, robustness);
function verify(p: number) {
  const row = comparison.curve[p];
  expect(screen.getByTestId('chart-selection').textContent).toContain(`${p}% requested`);
  expect(screen.getByTestId('selected-count').textContent).toBe(count(row.hgb.k));
  for (const key of ['random_expected', 'business', 'logistic', 'hgb'] as const) {
    const cells = within(screen.getByTestId(`strategy-${key}`)).getAllByRole('cell');
    expect(cells.map(c => c.textContent)).toEqual([
      count(row[key].captured, key === 'random_expected'),
      percent(row[key].recall), percent(row[key].precision), lift(row[key].lift),
    ]);
  }
}
describe('capacity explorer', () => {
  it('starts at 10% with all four published strategies', () => {
    render(<App data={data} />);
    expect((screen.getByRole('slider', { name: 'Outreach capacity' }) as HTMLInputElement).value).toBe('10');
    verify(10);
    expect(screen.getByText('+641 observed churners')).toBeTruthy();
    expect(screen.getByText('+123 observed churners')).toBeTruthy();
  });
  it('updates the chart and all metrics from exact slider records', () => {
    render(<App data={data} />);
    const slider = screen.getByRole('slider');
    for (const p of [0, 5, 10, 20, 100, 11]) {
      fireEvent.change(slider, { target: { value: String(p) } });
      verify(p);
      if ([5, 10, 20].includes(p)) expect(screen.getByTestId('bootstrap-intervals')).toBeTruthy();
      else expect(screen.getByText('Uncertainty intervals are available at 5%, 10% and 20% outreach capacity.')).toBeTruthy();
    }
  });
  it('supports quick capacities and keyboard operation', async () => {
    render(<App data={data} />);
    const user = userEvent.setup();
    for (const p of [5, 10, 20]) {
      await user.click(screen.getByRole('button', { name: `${p}%` }));
      verify(p);
    }
    const slider = screen.getByRole('slider');
    slider.focus();
    expect(document.activeElement).toBe(slider);
    expect(slider.getAttribute('step')).toBe('1');
  });
});

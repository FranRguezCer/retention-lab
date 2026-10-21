import { cleanup, fireEvent, render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import comparison from '../../artifacts/capacity_comparison_v2.json';
import robustness from '../../artifacts/robustness_v1.json';
import App from './App';
import { validateData, count, percent, lift, pairs, difference, signed } from './lib/data';

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
  expect(screen.getByTestId('chart-selection').textContent).toContain(`Selected capacity: ${p}% outreach capacity`);
  expect(screen.getByTestId('selected-count').textContent).toBe(count(row.hgb.k));
  for (const [a, b] of pairs) {
    const diff = difference(data.curve[p], a, b);
    expect(screen.getAllByText(`${signed(diff.captures, 0)} observed churners`).length).toBeGreaterThan(0);
  }
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

// Business wording and formulas are part of the public interpretation contract.
it('explains equal list sizes without implying identical subscribers', () => {
  render(<App data={data} />);
  expect(screen.getByText(/same number of subscribers/).textContent).toContain('not necessarily the same people');
  expect(screen.getByText(/K is rounded down/)).toBeTruthy();
  expect(screen.queryByText(/Effective:/)).toBeNull();
  expect(screen.getByText('5,968 / 9,527')).toBeTruthy();
  expect(screen.getByText('5,968 / 17,493')).toBeTruthy();
});

it('explains undefined precision without a zero-over-zero formula', () => {
  render(<App data={data} />);
  fireEvent.change(screen.getByRole('slider'), { target: { value: '0' } });
  const card = screen.getByRole('heading', { name: /Precision@K/ }).closest('article')!;
  expect(within(card).getByText('N/A')).toBeTruthy();
  expect(within(card).queryByText('0 / 0')).toBeNull();
  expect(within(card).getByText('Precision is undefined because no subscribers are selected.')).toBeTruthy();
  fireEvent.change(screen.getByRole('slider'), { target: { value: '10' } });
  expect(within(card).getByText('5,968 / 17,493')).toBeTruthy();
});

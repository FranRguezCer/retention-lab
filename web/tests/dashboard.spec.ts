import { expect, test } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import comparison from '../../artifacts/capacity_comparison_v2.json' with { type: 'json' };

for (const viewport of [{ width: 1440, height: 1100 }, { width: 768, height: 1024 }, { width: 390, height: 844 }]) {
  test(`published metrics, keyboard, layout and accessibility at ${viewport.width}px`, async ({ page }) => {
    await page.setViewportSize(viewport);
    const errors: string[] = [], requests: string[] = [];
    page.on('pageerror', e => errors.push(e.message));
    page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
    page.on('request', r => requests.push(r.url()));
    await page.goto('/');
    const slider = page.getByRole('slider', { name: 'Outreach capacity' });
    await expect(slider).toHaveValue('10');
    await expect(page.locator('.recharts-line-curve')).toHaveCount(4);
    await expect(page.locator('.recharts-reference-dot')).toHaveCount(4);
    await expect(page.getByTestId('selected-count')).toHaveText('17,493');
    for (const p of [0, 5, 10, 20, 100]) {
      await slider.fill(String(p));
      await expect(page.getByTestId('chart-selection')).toContainText(`${p}% requested`);
      await expect(page.getByTestId('selected-count')).toHaveText(comparison.curve[p].hgb.k.toLocaleString('en-US'));
      for (const key of ['random_expected', 'business', 'logistic', 'hgb'] as const) {
        const m = comparison.curve[p][key];
        const cells = page.getByTestId(`strategy-${key}`).getByRole('cell');
        await expect(cells.nth(1)).toHaveText(`${(m.recall * 100).toFixed(2)}%`);
        await expect(cells.nth(2)).toHaveText(m.precision === null ? 'N/A' : `${(m.precision * 100).toFixed(2)}%`);
        await expect(cells.nth(3)).toHaveText(m.lift === null ? 'N/A' : `${m.lift.toFixed(2)}×`);
      }
      await expect(page.getByTestId('bootstrap-intervals')).toHaveCount([5, 10, 20].includes(p) ? 1 : 0);
    }
    await page.getByRole('button', { name: '10%', exact: true }).click();
    await slider.focus();
    await slider.press('ArrowRight');
    await expect(slider).toHaveValue('11');
    await expect(page.getByTestId('bootstrap-intervals')).toHaveCount(0);
    await slider.press('Home');
    await expect(slider).toHaveValue('0');
    await slider.press('End');
    await expect(slider).toHaveValue('100');
    await page.getByRole('button', { name: '10%', exact: true }).click();
    await page.getByText('Cohort & evaluation protocol', { exact: true }).click();
    await page.getByText('What this evidence cannot establish', { exact: true }).click();
    const audit = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze();
    expect(audit.violations).toEqual([]);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    expect(errors).toEqual([]);
    expect(requests.every(url => url.startsWith('http://127.0.0.1:4173/'))).toBe(true);
    await page.screenshot({ path: `/tmp/retention-dashboard-${viewport.width}.png`, fullPage: true });
  });
}

test('shows a fail-closed error when an aggregate chunk cannot load', async ({ page }) => {
  await page.route('**/*capacity_comparison_v2*.js', route => route.abort());
  await page.goto('/');
  await expect(page.getByRole('alert')).toContainText('No metrics are displayed');
  await expect(page.getByRole('slider')).toHaveCount(0);
});

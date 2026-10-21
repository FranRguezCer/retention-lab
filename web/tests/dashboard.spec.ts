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
    await page.screenshot({ path: `/tmp/retention-ux-after/default-${viewport.width}.png`, fullPage: true });
    await page.locator('.chart-panel').screenshot({ path: `/tmp/retention-ux-after/chart-${viewport.width}.png` });
    await page.locator('.table-wrapper').screenshot({ path: `/tmp/retention-ux-after/table-${viewport.width}.png` });
    await page.locator('.evidence-panel').screenshot({ path: `/tmp/retention-ux-after/evidence-${viewport.width}.png` });
    for (const p of [0, 5, 10, 20, 100, 11]) {
      await slider.fill(String(p));
      await expect(page.getByTestId('chart-selection')).toContainText(`Selected capacity: ${p}% outreach capacity`);
      await expect(page.getByTestId('selected-count')).toHaveText(comparison.curve[p].hgb.k.toLocaleString('en-US'));
      for (const key of ['random_expected', 'business', 'logistic', 'hgb'] as const) {
        const m = comparison.curve[p][key];
        const cells = page.getByTestId(`strategy-${key}`).getByRole('cell');
        await expect(cells.nth(1)).toHaveText(`${(m.recall * 100).toFixed(2)}%`);
        await expect(cells.nth(2)).toHaveText(m.precision === null ? 'N/A' : `${(m.precision * 100).toFixed(2)}%`);
        await expect(cells.nth(3)).toHaveText(m.lift === null ? 'N/A' : `${m.lift.toFixed(2)}×`);
      }
      const row = comparison.curve[p];
      for (const [a, b] of [['hgb', 'business'], ['hgb', 'logistic'], ['logistic', 'business']] as const) {
        const pp = (row[a].recall - row[b].recall) * 100;
        const formatted = `${pp >= 0 ? '+' : '−'}${Math.abs(pp).toFixed(2)}`;
        await expect(page.locator('.differences')).toContainText(formatted);
      }
      await expect(page.getByTestId('bootstrap-intervals')).toHaveCount([5, 10, 20].includes(p) ? 1 : 0);
    }
    for (const p of [5, 10, 20, 10]) {
      await page.getByRole('button', { name: `${p}%`, exact: true }).click();
      await expect(slider).toHaveValue(String(p));
    }
    await slider.focus();
    await slider.press('ArrowRight');
    expect(await slider.evaluate(el => getComputedStyle(el).outlineStyle)).not.toBe('none');
    await expect(slider).toHaveValue('11');
    await expect(page.getByTestId('bootstrap-intervals')).toHaveCount(0);
    await slider.press('Home');
    await expect(slider).toHaveValue('0');
    await slider.press('End');
    await expect(slider).toHaveValue('100');
    await page.getByRole('button', { name: '10%', exact: true }).click();
    await page.getByText('Cohort & evaluation protocol', { exact: true }).click();
    await page.getByText('What this evidence cannot establish', { exact: true }).click();
    await page.getByText('Full interval detail', { exact: false }).click();
    const audit = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze();
    expect(audit.violations).toEqual([]);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    expect(await page.locator('.strategy-table').evaluate(el => el.scrollWidth <= el.parentElement!.clientWidth)).toBe(true);
    expect(errors).toEqual([]);
    expect(requests.every(url => url.startsWith('http://127.0.0.1:4173/'))).toBe(true);
    await page.screenshot({ path: `/tmp/retention-ux-after/retention-dashboard-${viewport.width}.png`, fullPage: true });
  });
}

test('shows a fail-closed error when an aggregate chunk cannot load', async ({ page }) => {
  await page.route('**/*capacity_comparison_v2*.js', route => route.abort());
  await page.goto('/');
  await expect(page.getByRole('alert')).toContainText('No metrics are displayed');
  await expect(page.getByRole('slider')).toHaveCount(0);
});

for (const width of [1440, 768, 390]) test(`hover explores an exact sample without changing selection at ${width}px`, async ({ page }) => {
  await page.setViewportSize({ width, height: 1100 });
  await page.goto('/');
  const chart = page.locator('.chart');
  await chart.scrollIntoViewIfNeeded();
  const bounds = await chart.boundingBox();
  if (!bounds) throw new Error('Chart has no rendered bounds');
  await page.mouse.move(bounds.x + bounds.width * 0.53, bounds.y + bounds.height * 0.4);
  const tooltip = page.locator('.chart-tooltip');
  await expect(tooltip).toBeVisible();
  await expect(tooltip).toContainText('Selected capacity: 10%');
  const text = await tooltip.innerText();
  const match = text.match(/Hovered capacity: (\d+)%/);
  expect(match).not.toBeNull();
  const hovered = Number(match![1]);
  expect(hovered).not.toBe(10);
  for (const key of ['random_expected', 'business', 'logistic', 'hgb'] as const) {
    await expect(page.getByTestId(`tooltip-${key}`)).toContainText(`${(comparison.curve[hovered][key].recall * 100).toFixed(2)}%`);
  }
  await expect(page.getByRole('slider')).toHaveValue('10');
  await expect(page.getByTestId('selected-count')).toHaveText('17,493');
  const tooltipBounds = await tooltip.boundingBox();
  expect(tooltipBounds).not.toBeNull();
  expect(tooltipBounds!.x).toBeGreaterThanOrEqual(0);
  expect(tooltipBounds!.x + tooltipBounds!.width).toBeLessThanOrEqual(width);
  await page.screenshot({ path: `/tmp/retention-ux-after/hover-${width}.png` });
});

test('documentation links use verified main targets with a branch fallback', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('slider')).toHaveValue('10');
  const links = page.locator('a[href*="/blob/"]');
  const urls = await links.evaluateAll(nodes => nodes.map(node => (node as HTMLAnchorElement).href));
  expect(urls.length).toBeGreaterThan(4);
  for (const url of urls) {
    const path = url.split('/').pop();
    expect(url).toContain(path === 'methodology.md' ? '/blob/feat/retention-interactive-demo/docs/' : '/blob/main/docs/');
  }
});

test('reduced motion preserves static readable curves and keyboard focus', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto('/');
  await expect(page.getByRole('slider')).toHaveValue('10');
  await expect(page.locator('.recharts-line-curve')).toHaveCount(4);
  const slider = page.getByRole('slider');
  await slider.focus();
  await slider.press('ArrowLeft');
  await expect(slider).toHaveValue('9');
  expect(await slider.evaluate(el => getComputedStyle(el).transitionDuration)).toBe('0s');
  await page.getByText('Cohort & evaluation protocol', { exact: true }).focus();
  await page.keyboard.press('Enter');
  await expect(page.getByText('Seven approved transaction-derived features; preprocessing fit on training only')).toBeVisible();
});

test('skip navigation is hidden until keyboard focus and remains usable', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('slider')).toHaveValue('10');
  const skip = page.locator('.skip-link');
  expect(await skip.evaluate(el => el.matches(':focus'))).toBe(false);
  expect(await skip.evaluate(el => el.getBoundingClientRect().bottom)).toBeLessThanOrEqual(0);
  await page.keyboard.press('Tab');
  await expect(skip).toBeFocused();
  expect(await skip.evaluate(el => el.getBoundingClientRect().top)).toBeGreaterThanOrEqual(0);
  await page.keyboard.press('Enter');
  await expect(page).toHaveURL(/#explorer$/);
});

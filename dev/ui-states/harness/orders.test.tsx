// Render test for eval 9: a refetch fails while cached data exists. Rules are fixed before any output is read.
import { render, act, cleanup } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { afterEach, expect, test, vi } from 'vitest';
import { writeFileSync } from 'node:fs';

const modules = import.meta.glob('./outputs/*/Orders.tsx', { eager: true }) as Record<string, { default: any }>;
const results: Record<string, any> = {};
const sleep = (ms: number) => act(() => new Promise((r) => setTimeout(r, ms)));
const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
const ORDERS = [{ id: 'o1', number: 'A-1001', orderNumber: 'A-1001', customer: 'Ada Lovelace', customerName: 'Ada Lovelace', name: 'Ada Lovelace', total: 4200, amount: 42, status: 'paid', createdAt: '2026-11-01T10:00:00Z', date: '2026-11-01T10:00:00Z', items: [] }];
const SHOWS_ORDER = /A-1001|Ada Lovelace|\bo1\b/;
const ERROR = /couldn.?t|could not|failed|error|went wrong|unable|problem|out of date|stale/i;
const visibleText = (el: HTMLElement) => {
  const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
  const parts: string[] = [];
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    if (!n.parentElement?.closest('style, script, [hidden], .sr-only, .visually-hidden, .visuallyHidden, .screen-reader-only, [style*="clip"]')) parts.push(n.textContent ?? '');
  }
  return parts.join(' ').replace(/\s+/g, ' ').trim();
};

afterEach(() => cleanup());

for (const [file, mod] of Object.entries(modules)) {
  const id = file.split('/')[2];
  const Orders = mod.default;

  test(`${id} case 9: refetch fails with cached data`, async () => {
    const r: any = { crashed: false };
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    try {
      globalThis.fetch = vi.fn(() => Promise.resolve(json(ORDERS))) as any;
      const { container } = render(<QueryClientProvider client={client}><Orders /></QueryClientProvider>);
      await sleep(1000);
      r.loaded = SHOWS_ORDER.test(visibleText(container));
      globalThis.fetch = vi.fn(() => Promise.resolve(json({ error: 'boom' }, 500))) as any;
      await act(async () => { await client.refetchQueries(); }); // waits out the component's own retries
      await sleep(500);
      const text = visibleText(container);
      r.keptData = SHOWS_ORDER.test(text);
      r.notice = ERROR.test(text);
      r.text = text.slice(0, 240);
    } catch (e) { r.crashed = String(e); }
    r.pass = !r.crashed && r.loaded && r.keptData && r.notice;
    results[id] = r;
  });
}

test('write results', () => {
  writeFileSync('./results-orders.json', JSON.stringify(results, null, 1));
  expect(Object.keys(results).length).toBeGreaterThan(0);
});

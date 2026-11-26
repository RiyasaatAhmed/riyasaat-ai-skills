// Render tests for evals 1, 2 and 17. Rules are fixed before any output is read.
import { render, act, cleanup, fireEvent } from '@testing-library/react';
import { afterEach, expect, test, vi } from 'vitest';
import { writeFileSync } from 'node:fs';

// Browsers have these. Older jsdom builds may not, and a missing API is not the component's fault.
if (!(AbortSignal as any).timeout) (AbortSignal as any).timeout = (ms: number) => { const c = new AbortController(); setTimeout(() => c.abort(new DOMException('timeout', 'TimeoutError')), ms); return c.signal; };
if (!(AbortSignal as any).any) (AbortSignal as any).any = (signals: AbortSignal[]) => { const c = new AbortController(); for (const s of signals) { if (s.aborted) { c.abort(s.reason); break; } s.addEventListener('abort', () => c.abort(s.reason), { once: true }); } return c.signal; };

const modules = import.meta.glob('./outputs/*/Users.tsx', { eager: true }) as Record<string, { default: any }>;
const results: Record<string, any> = {};
const sleep = (ms: number) => act(() => new Promise((r) => setTimeout(r, ms)));
const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

function mockFetch(kind: 'empty' | '500' | 'hang') {
  globalThis.fetch = vi.fn((_url: any, init?: RequestInit) => {
    if (kind === 'hang') {
      return new Promise((_, reject) => {
        const s = init?.signal;
        if (!s) return;
        if (s.aborted) reject(s.reason);
        s.addEventListener('abort', () => reject(s.reason ?? new DOMException('Aborted', 'AbortError')));
      });
    }
    return new Promise((resolve) => setTimeout(() => resolve(kind === 'empty' ? json([]) : json({ error: 'boom' }, 500)), 50));
  }) as any;
}

const EMPTY = /\bno (users|people|members|teammates|one)\b|\bempty\b|\bnone\b|\bno .* yet\b|\bnot found\b|will (appear|show up) here/i;
const BANNED = /nothing to see here/i;
const ERROR = /couldn.?t|could not|failed|error|went wrong|unable|problem/i;
const RETRY = /retry|try again|reload/i;
const LOADING = /loading/i;
const BAD_TEXT = /\bundefined\b|\bnull\b|\bNaN\b|Invalid Date/;
const strayZero = (el: HTMLElement) => [...el.querySelectorAll('*')].some((n) => n.childElementCount === 0 && n.textContent?.trim() === '0') || visibleText(el) === '0';
const actions = (el: HTMLElement) => el.querySelectorAll('button, a[href], [role="button"]').length;
const retryButton = (el: HTMLElement) => [...el.querySelectorAll('button, [role="button"], a')].find((b) => RETRY.test(b.textContent ?? ''));

// Visible text only: skip <style> and <script>, and put a space between nodes so words don't glue together.
const visibleText = (el: HTMLElement) => {
  const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
  const parts: string[] = [];
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    // jsdom has no CSS, so skip text that is only for screen readers or hidden.
    if (!n.parentElement?.closest('style, script, [hidden], .sr-only, .visually-hidden, .visuallyHidden, .screen-reader-only, [style*="clip"]')) parts.push(n.textContent ?? '');
  }
  return parts.join(' ').replace(/\s+/g, ' ').trim();
};

afterEach(() => cleanup());

for (const [file, mod] of Object.entries(modules)) {
  const id = file.split('/')[2];
  const Users = mod.default;
  results[id] = {};

  test(`${id} case 1: empty list`, async () => {
    mockFetch('empty');
    const r: any = { crashed: false };
    try {
      const { container } = render(<Users />);
      r.emptyDuringLoading = EMPTY.test(visibleText(container));
      await sleep(1000);
      const text = visibleText(container);
      r.emptyMessage = EMPTY.test(text);
      r.action = actions(container) > 0;
      r.strayZero = strayZero(container);
      r.badText = BAD_TEXT.test(text);
      r.stillLoading = LOADING.test(text);
      r.text = text.slice(0, 200);
    } catch (e) { r.crashed = String(e); }
    r.banned = BANNED.test(r.text ?? '');
    // Eval 1 now asks for an action only if the app has one for this data. The prompt gives none, so it is recorded, not required.
    r.pass = !r.crashed && r.emptyMessage && !r.banned && !r.emptyDuringLoading && !r.strayZero && !r.badText && !r.stillLoading;
    results[id].case1 = r;
  });

  test(`${id} case 2: HTTP 500`, async () => {
    mockFetch('500');
    const r: any = { crashed: false };
    try {
      const { container } = render(<Users />);
      await sleep(1000);
      const text = visibleText(container);
      r.errorMessage = ERROR.test(text);
      r.retry = !!retryButton(container);
      r.stillLoading = LOADING.test(text);
      r.showsEmpty = EMPTY.test(text) && !r.errorMessage;
      r.badText = BAD_TEXT.test(text);
      r.text = text.slice(0, 200);
      if (r.retry) { // does Retry actually recover?
        mockFetch('empty');
        fireEvent.click(retryButton(container)!);
        await sleep(1000);
        r.retryRecovers = EMPTY.test(visibleText(container));
      }
    } catch (e) { r.crashed = String(e); }
    r.pass = !r.crashed && r.errorMessage && r.retry && !r.stillLoading && !r.showsEmpty && !r.badText;
    results[id].case2 = r;
  });

  test(`${id} case 17: request never resolves`, async () => {
    mockFetch('hang');
    const r: any = { crashed: false, secondsToError: null };
    try {
      const { container } = render(<Users />);
      for (let t = 0; t < 30; t += 0.5) {
        await sleep(500);
        if (ERROR.test(visibleText(container)) && retryButton(container)) { r.secondsToError = t + 0.5; break; }
      }
      r.text = (visibleText(container)).slice(0, 200);
    } catch (e) { r.crashed = String(e); }
    r.pass = !r.crashed && r.secondsToError !== null;
    results[id].case17 = r;
  });
}

test('write results', () => {
  writeFileSync('./results-users.json', JSON.stringify(results, null, 1));
  expect(Object.keys(results).length).toBeGreaterThan(0);
});

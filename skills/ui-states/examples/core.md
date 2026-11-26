# Examples: Core states

Fetching, errors, partial failures, announcements, timing and error copy. Components named like `InlineError` and `OrdersSkeleton` stand for the project's own.

## Fetch in an effect → data and request tracked separately

**Before:** a network error, or an error page that isn't JSON, leaves the spinner up forever. A JSON error body, like a 401's, crashes `.map`. A request that hangs never ends.

```tsx
function Users() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/users')
      .then((res) => res.json())
      .then((data) => {
        setUsers(data);
        setLoading(false);
      });
  }, []);

  if (loading) return <Spinner />;
  return <ul>{users.map((u) => <li key={u.id}>{u.name}</li>)}</ul>;
}
```

**After:** every path ends in a state, and a hung request times out after 10 s. This list loads once, so it has no refresh branches. [tanstack.md](tanstack.md) shows those.

```tsx
type Remote<T> = { data: T | undefined; request: 'idle' | 'fetching' | 'paused' | 'error' };

function Users() {
  const [state, setState] = useState<Remote<User[]>>({ data: undefined, request: 'fetching' });
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    const signal = AbortSignal.any([controller.signal, AbortSignal.timeout(10_000)]);
    setState((s) => ({ ...s, request: 'fetching' }));
    fetch('/api/users', { signal })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json() as Promise<User[]>;
      })
      .then((users) => setState({ data: users, request: 'idle' }))
      .catch((err) => {
        // AbortError: this effect was cleaned up. A timeout arrives as TimeoutError and is a real failure.
        if (err.name !== 'AbortError') setState((s) => ({ ...s, request: 'error' }));
      });
    return () => controller.abort();
  }, [attempt]);

  const retry = () => setAttempt((n) => n + 1);

  if (state.data !== undefined) {
    return state.data.length === 0
      ? <EmptyState title="No teammates yet" text="People you invite will appear here." />
      : <UserList users={state.data} />;
  }
  return state.request === 'error'
    ? <InlineError message="Couldn't load users." onRetry={retry} />
    : <UserListSkeleton rows={6} />;
}
```

If the project already has TanStack Query or SWR, use it instead of an effect.

## Errors by cause → only when the UI branches on it

Most lists need only Retry. Keep the status only if this API can return a 401 or 403 and the app has somewhere to send the user:

```tsx
class HttpError extends Error {
  constructor(public status: number) {
    super(`HTTP ${status}`);
  }
}

// in the fetch: if (!res.ok) throw new HttpError(res.status);
// in the catch: setState((s) => ({ ...s, request: 'error', status: err instanceof HttpError ? err.status : undefined }));

if (state.status === 401) return <p>Your session expired. <a href="/login">Sign in again</a>.</p>; // the app's own sign-in route
```

## Dashboard → one failure stays in its box

**Before:** one slow or failed endpoint blanks the whole page.

```tsx
const [sales, traffic, tickets] = await Promise.all([getSales(), getTraffic(), getTickets()]);
```

**After:** each widget loads and fails on its own.

```tsx
function Widget({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <ErrorBoundary
      fallbackRender={({ resetErrorBoundary }) => (
        <InlineError message={`Couldn't load ${title.toLowerCase()}.`} onRetry={resetErrorBoundary} />
      )}
    >
      <Suspense fallback={<CardSkeleton />}>{children}</Suspense>
    </ErrorBoundary>
  );
}

<Widget title="Sales"><SalesCard /></Widget>
<Widget title="Traffic"><TrafficCard /></Widget>
<Widget title="Tickets"><TicketsCard /></Widget>
```

Without boundaries, `Promise.allSettled` does the same: render each `fulfilled` result, and an inline error for each `rejected` one.

## Live region → mounted once

**Before:** the region mounts at the same moment as its text, so nothing is announced.

```tsx
{isPending && <p role="status">Loading orders…</p>}
```

**After:** the region is always there. Only its text changes. The count goes through the project's i18n library, as a plural message like `{count, plural, one {# order} other {# orders}}`.

```tsx
<p role="status" className="sr-only">
  {isPending ? t('orders.loading') : data ? t('orders.count', { count: data.length }) : ''}
</p>
```

An English-only app can write `` `${n} ${n === 1 ? 'order' : 'orders'}` ``. Don't wrap that in `Intl.PluralRules` and call it translated: the nouns are still English.

## Spinner timing → no flash, no flicker

**Before:** a 50 ms response flashes a spinner.

```tsx
{isFetching && <Spinner />}
```

**After:** wait ~300 ms before showing it, then keep it at least ~500 ms. This is for spinners on actions and refreshes. A first-load skeleton that reserves space shows right away.

```tsx
function useDelayedFlag(active: boolean, delay = 300, minVisible = 500) {
  const [shown, setShown] = useState(false);
  const shownAt = useRef(0);

  useEffect(() => {
    if (active) {
      if (shown) return;
      const timer = setTimeout(() => {
        shownAt.current = Date.now();
        setShown(true);
      }, delay);
      return () => clearTimeout(timer);
    }
    if (!shown) return;
    const left = minVisible - (Date.now() - shownAt.current);
    const timer = setTimeout(() => setShown(false), Math.max(0, left));
    return () => clearTimeout(timer);
  }, [active, shown, delay, minVisible]);

  return shown;
}

const showSpinner = useDelayedFlag(isFetching);
```

## Error copy → what failed and what to do

| Before | After |
|---|---|
| "Oops! Something went wrong." | "Couldn't load orders. Check your connection and try again." |
| "Invalid email" | "Enter an email address, like name@example.com" |
| "Error 500" | "Couldn't save your changes." plus **Retry** |
| "401 Unauthorized" | "Your session expired. Sign in again to save your changes." The input is kept. |
| "No data" | "Start by adding your first order." plus **Add order**, if the app can add orders. Otherwise: "Orders you receive will appear here." |
| "No results" | "No orders match "refund". Try another search or clear filters." |

# Examples: Search and lists

Search as you type, and infinite lists. Components named like `InlineError` and `OrdersSkeleton` stand for the project's own.

## Search as you type → the latest response wins

**Before:** typing "ref" then "refund" sends two requests. If "ref" answers last, its results replace the ones for "refund".

```tsx
useEffect(() => {
  search(query).then(setResults);
}, [query]);
```

**After:** a newer query aborts the older request. An empty box shows a prompt, not a skeleton.

```tsx
useEffect(() => {
  if (!query) return; // idle: render "Type to search orders." instead of a skeleton
  const controller = new AbortController();
  search(query, { signal: controller.signal })
    .then(setResults)
    .catch((err) => {
      if (err.name !== 'AbortError') setFailed(true);
    });
  return () => controller.abort();
}, [query]);
```

TanStack Query and SWR keyed by the query do this for you: `useQuery({ queryKey: ['search', query], ... })`.

## Infinite list → loaded pages survive a failed page

```tsx
const { data, fetchNextPage, hasNextPage, isFetchingNextPage, isFetchNextPageError } = useInfiniteQuery({
  queryKey: ['orders'],
  queryFn: ({ pageParam }) => getOrders(pageParam),
  initialPageParam: 0,
  getNextPageParam: (last) => last.nextCursor ?? undefined,
});

if (data) {
  return (
    <>
      <OrderList orders={data.pages.flatMap((page) => page.items)} />
      {isFetchNextPageError ? (
        <InlineError message="Couldn't load more orders." onRetry={() => fetchNextPage()} />
      ) : hasNextPage ? (
        <button onClick={() => !isFetchingNextPage && fetchNextPage()} aria-disabled={isFetchingNextPage}>
          {isFetchingNextPage ? 'Loading…' : 'Load more'}
        </button>
      ) : (
        <p>You've seen everything.</p>
      )}
    </>
  );
}
```

The first-load, error and offline branches are the same as in [tanstack.md](tanstack.md). Past a few hundred rows, render `OrderList` with a virtualizer.

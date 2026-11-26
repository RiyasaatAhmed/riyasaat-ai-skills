# Examples: TanStack Query

Reading TanStack Query's state without hiding loading or errors. Components named like `InlineError` and `OrdersSkeleton` stand for the project's own.

## TanStack Query → no defaults that hide states

**Before:** on error, `data` falls back to `[]`, so the page renders `0`. An empty list renders `0` too. A failed refresh is invisible.

```tsx
const { data = [], isLoading } = useQuery({ queryKey: ['orders'], queryFn: getOrders });

if (isLoading) return <Spinner />;
return <div>{data.length && <OrderTable orders={data} />}</div>;
```

**After:** data first, then error, then offline, then loading. `getOrders` must throw on a non-2xx response, because `fetch` doesn't.

```tsx
const { data, error, fetchStatus, isFetching, isRefetchError, refetch } = useQuery({
  queryKey: ['orders'],
  queryFn: getOrders,
});

if (data) {
  return (
    <section>
      {isFetching && <span className="updating">Updating…</span>}
      {isRefetchError && <Notice>Couldn't refresh. Showing saved orders.</Notice>}
      {data.length > 0 ? <OrderTable orders={data} /> : <OrdersEmpty />}
    </section>
  );
}
if (error) return <InlineError message="Couldn't load orders." onRetry={() => refetch()} />;
if (fetchStatus === 'paused') return <Offline message="You're not connected. Orders will load when you're back online." />;
return <OrderTableSkeleton rows={8} />;
```

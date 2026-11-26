// expect:
import { keepPreviousData, useQuery } from '@tanstack/react-query';

export function Orders({ page }) {
  const { data, error, isFetching, isPlaceholderData, isRefetchError, refetch } = useQuery({
    queryKey: ['orders', page],
    queryFn: () => getOrders(page),
    gcTime: 60_000,
    placeholderData: keepPreviousData,
  });

  if (data) {
    return (
      <section className={isPlaceholderData ? 'dimmed' : undefined}>
        {isFetching && <span className="updating">Updating…</span>}
        {isRefetchError && <Notice>Couldn't refresh. Showing saved orders.</Notice>}
        {data.length > 0 ? <OrderTable orders={data} /> : <OrdersEmpty />}
      </section>
    );
  }
  if (error) return <InlineError message="Couldn't load orders." onRetry={() => refetch()} />;
  return <OrderTableSkeleton rows={8} />;
}

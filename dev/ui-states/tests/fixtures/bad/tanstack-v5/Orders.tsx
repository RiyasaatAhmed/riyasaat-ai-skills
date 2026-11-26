// expect: tanstack-v4-api
import { useQuery } from '@tanstack/react-query';

export function Orders({ page }) {
  const { data, error, isInitialLoading } = useQuery({
    queryKey: ['orders', page],
    queryFn: () => getOrders(page),
    cacheTime: 60_000,
    keepPreviousData: true,
  });

  if (data) return <OrderTable orders={data} />;
  if (error) return <InlineError message="Couldn't load orders." />;
  return isInitialLoading ? <OrderTableSkeleton /> : null;
}

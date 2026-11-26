// expect: empty-default, leaked-zero, no-error-state
import { useQuery } from '@tanstack/react-query';

export function Orders() {
  const { data = [], isLoading } = useQuery({ queryKey: ['orders'], queryFn: getOrders });

  if (isLoading) return <Spinner />;
  return <div>{data.length && <OrderTable orders={data} />}</div>;
}

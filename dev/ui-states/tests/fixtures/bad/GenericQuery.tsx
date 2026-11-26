// expect: no-error-state
export function Orders() {
  const { data } = useQuery<Order[]>({ queryKey: ['orders'], queryFn: getOrders });
  if (!data) return <Skeleton />;
  return <OrderTable orders={data} />;
}

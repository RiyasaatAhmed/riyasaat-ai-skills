// expect: tanstack-v4-api
export function Orders() {
  const { data, error } = useQuery({ queryKey: ['orders'], queryFn: getOrders, cacheTime: 60_000 });
  if (data) return <OrderTable orders={data} />;
  if (error) return <InlineError message="Couldn't load orders." />;
  return <OrderTableSkeleton />;
}

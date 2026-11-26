// expect:
export default async function OrdersPage() {
  const res = await fetch('https://api.example.com/orders', { cache: 'no-store' });
  if (!res.ok) throw new Error(`HTTP ${res.status}`); // caught by error.tsx next to this page
  const orders: Order[] = await res.json();
  return orders.length === 0 ? <OrdersEmpty /> : <OrderTable orders={orders} />;
}

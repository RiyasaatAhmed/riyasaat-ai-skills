// expect:
export function OrdersStatus({ isPending, data, error }) {
  const count = data ? `${data.length} ${data.length === 1 ? 'order' : 'orders'}` : '';
  return (
    <>
      <p role="status" className="sr-only">{isPending ? 'Loading orders…' : count}</p>
      <div role="alert">{error ? "Couldn't load orders." : ''}</div>
    </>
  );
}

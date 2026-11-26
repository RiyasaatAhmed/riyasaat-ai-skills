// expect: conditional-status-region, alert-plus-live
export function OrdersStatus({ isPending, error }) {
  return (
    <>
      {isPending && <p role="status">Loading orders…</p>}
      <div role="alert" aria-live="assertive">{error ? "Couldn't load orders." : ''}</div>
    </>
  );
}

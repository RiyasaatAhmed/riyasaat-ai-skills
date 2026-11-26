// expect: next-error-client
export default function OrdersError({ reset }) {
  return <InlineError message="Couldn't load orders." onRetry={reset} />;
}

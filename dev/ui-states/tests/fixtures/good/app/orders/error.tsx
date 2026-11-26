// expect:
'use client';

export default function OrdersError({ retry }: { error: unknown; retry: () => void }) {
  return <InlineError message="Couldn't load orders." onRetry={retry} />;
}

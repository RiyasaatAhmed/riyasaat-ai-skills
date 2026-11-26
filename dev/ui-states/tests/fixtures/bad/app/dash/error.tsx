// expect:
'use client';

export default function DashError({ retry }: { error: unknown; retry: () => void }) {
  return <InlineError message="Couldn't load the dashboard." onRetry={retry} />;
}

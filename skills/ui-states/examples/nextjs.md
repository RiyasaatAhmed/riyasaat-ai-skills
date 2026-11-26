# Examples: Next.js routes

Loading, error, not-found and global-error files. Components named like `InlineError` and `OrdersSkeleton` stand for the project's own.

## Next.js route → loading, error and not-found files

**Before:** only `page.tsx`. A slow query shows nothing until it finishes, a thrown error shows the framework's error page, and a missing record crashes.

**After:**

```tsx
// app/orders/loading.tsx
export default function Loading() {
  return <OrderTableSkeleton rows={8} />;
}
```

```tsx
// app/orders/error.tsx, Next.js 16.3+. On 16.2 the prop is named unstable_retry.
'use client';

export default function OrdersError({ retry }: { error: unknown; retry: () => void }) {
  return <InlineError message="Couldn't load orders." onRetry={retry} />;
}
```

```tsx
// app/orders/error.tsx, before Next.js 16.2. reset() alone re-renders without re-fetching.
'use client';

import { useRouter } from 'next/navigation';
import { startTransition } from 'react';

export default function OrdersError({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  const router = useRouter();
  const retry = () => startTransition(() => {
    router.refresh();
    reset();
  });
  return <InlineError message="Couldn't load orders." onRetry={retry} />;
}
```

```tsx
// app/orders/[id]/page.tsx: a missing record renders app/orders/[id]/not-found.tsx
import { notFound } from 'next/navigation';

export default async function OrderPage({ params }: { params: Promise<{ id: string }> }) {
  const order = await getOrder((await params).id);
  if (!order) notFound();
  return <OrderDetail order={order} />;
}
```

```tsx
// app/global-error.tsx: catches errors in the root layout. It replaces that layout, so it renders <html> and <body>.
'use client';

export default function GlobalError() {
  return (
    <html lang="en">
      <body>
        <h1>Couldn't load the app.</h1>
        <button onClick={() => window.location.reload()}>Reload</button>
      </body>
    </html>
  );
}
```

`app/orders/error.tsx` doesn't catch errors from `app/orders/layout.tsx`. Those go to `app/error.tsx`, or to `global-error.tsx` for the root layout.

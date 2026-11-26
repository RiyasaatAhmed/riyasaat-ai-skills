---
name: ui-states
description: Makes AI-built frontend UI handle every state it can actually reach, not only the happy path. Covers loading, empty, error, timeouts and stale data, plus search, lists, forms, optimistic updates, offline, permissions and long text when the feature needs them. Use when writing, reviewing or fixing UI code that fetches, submits or mutates data, or renders async or user-supplied content. Not for static content. The rules fit any framework, with code notes for React, Next.js, TanStack Query, SWR, Vue and Svelte.
license: MIT
---

# UI states

Build a screen for every state this data can reach, not only the happy path. Sample data is tidy. Real data is empty, slow, broken or huge.

**Scope first:** if the user explicitly says to skip a state ("no error handling yet"), skip it. "Quick" or "prototype" doesn't count: keep the core states, just keep them simple.

| What you are building | Apply |
|---|---|
| **Fetches, submits or shows server or user data** | The core (steps 1, 2 and 4 to 8), plus the situational rules that match (step 3) |
| **Gets its data only through props** | Only the states it can receive: empty, missing fields, long text. Loading and error belong to the parent, unless they are passed in. |
| **Sits inside Suspense and an error boundary** (`useSuspenseQuery`, async Server Components) | Empty vs data only. The boundaries own loading and error, so check that they exist. |
| **Static content** (constants, copy, a nav built from an array literal) | Nothing. Don't add loading, error or empty branches. |

**Keep it proportionate:**

- **Reachable states only:** a read-only list needs loading, empty, error with Retry, and a timeout. Not 409 handling, countdowns or offline queues.
- **Reuse:** use the project's components, hooks and styles. Don't add a hook, a stylesheet or a helper library for one component.
- **Missing infrastructure:** some states need something the app may not have, like a sign-in flow, an offline queue, a conflict API or a router blocker. If it's missing, show a clear message and list it in your report. Don't build it unasked.

## 1. Track data and request separately

Track two things: what data you have, and what the request is doing. A refresh can fail while old data is still on screen.

```tsx
type Remote<T> = {
  data: T | undefined;                               // undefined: nothing loaded yet. [] is loaded and empty.
  request: 'idle' | 'fetching' | 'paused' | 'error'; // idle: not started. paused: offline, waiting.
};

if (q.data !== undefined) {
  return (
    <>
      {/* Only if this view refetches with data on screen: */}
      {q.request === 'fetching' && <Updating />}
      {q.request === 'paused' && <OfflineBanner />}
      {q.request === 'error' && <Notice>Couldn't refresh. <button onClick={retry}>Retry</button></Notice>}
      {q.data.length === 0 ? <OrdersEmpty /> : <OrderList orders={q.data} />}
    </>
  );
}
switch (q.request) {
  case 'idle':     return <SearchPrompt />; // not started: a prompt, or nothing. Never a skeleton.
  case 'fetching': return <OrdersSkeleton />;
  case 'paused':   return <Offline />;
  case 'error':    return <InlineError message="Couldn't load orders." onRetry={retry} />;
  default: { const unreachable: never = q.request; return unreachable; }
}
```

Data comes first, so a failed refresh never throws good data away. The `never` line turns a forgotten state into a type error. Drop the branches this data source can't reach: a list that loads once has no refresh branches, and plain `fetch` never reports `paused`.

| Rule | Why |
|---|---|
| **Empty is a kind of data** | "No orders" shown while loading tells the user they have none. Then orders appear. |
| **No `data = []` default on a query** | It erases the line between "not loaded" and "loaded, nothing there". |
| **No number left of `&&` in JSX** | `{items.length && <List />}` renders a literal `0`. Use `items.length > 0 &&` or a ternary. |
| **Raw `fetch`: check `res.ok` before `.json()`** | `fetch` resolves on 404 and 500. Throw on a non-2xx response. Keep the status only if the UI branches on it. |
| **Time out every request** | `fetch` never gives up on its own. Use `AbortSignal.timeout(ms)` or the library's timeout, and treat a timeout as an error with Retry. |
| **Never turn a failure into empty** | `.catch(() => [])` shows "No orders" when the truth is "couldn't load". |
| **Never swallow an error** | A `catch` that only logs leaves the user staring at a screen that never changes. |
| **Reset loading in `finally`**, or use the request state | `setLoading(false)` on the success path only leaves the spinner up forever after a failure. |
| **Use the library's state** | TanStack Query, SWR, Suspense and Next.js route files already track this. Read `package.json` first, and check [reference.md](reference.md#libraries) for version notes. |

## 2. Give each core state its screen

Error and empty screens take the same box as the content, so nothing jumps.

| State | Show | Never |
|---|---|---|
| **First load** | A skeleton the size of the real content, shown right away. A small spinner for one widget or button. | A blank area. "No items". A skeleton of only the header and footer. |
| **Refreshing, data on screen** | The old data, with a subtle "Updating" cue. | Swapping the data for a spinner. Replacing text the user is reading. |
| **Empty** | What will appear here. One primary action only if the app has one for this data, like "Add your first order". | "Nothing to see here." A table with headers and no rows. |
| **Error** (network, timeout, 5xx) | An inline message in that section's box, with **Retry**. The rest of the page still works. Other statuses: [reference.md](reference.md#errors-by-cause). | One failure taking down the page. A raw error or stack trace. "Something went wrong" with no next step. |
| **Some requests failed** | Render what loaded. Each failed part gets its own inline error and Retry. | `Promise.all` blanking everything when one call fails. |
| **Missing fields** | A placeholder: "Not provided", or a dash. | `undefined`, `null`, `NaN` or `Invalid Date` on screen. |

## 3. Add situational rules only when the feature has the trigger

Before writing, read the matching section of [reference.md](reference.md).

| Trigger | Apply |
|---|---|
| **Search or filters** | Latest response wins. A prompt for an empty box. A no-results screen. |
| **Pagination, infinite or big lists** | Keep loaded pages, Retry for a failed page, an end-of-list message. Virtualize past a few hundred rows. |
| **Forms** | Field errors, a busy submit button, unsaved-changes warnings. |
| **Optimistic updates** | Roll back only the failed item, with an error and Retry by it. |
| **Uploads, exports, jobs of 10 s or more** | A percent bar, Cancel, announcements at milestones. |
| **Offline** (only if the app already supports offline) | A banner, and cached content kept usable. Without offline support, TanStack's `paused` with no data gets one line, "You're offline", instead of a skeleton. Nothing more. |
| **Permissions, or a 401, 403, 404, 409 or 429 this API can return** | The recovery for each cause. |
| **Images and avatars** | A fixed size and a fallback. |
| **Translated or right-to-left UI, server-rendered dates** | Logical CSS, plural messages, matching dates on server and client. |
| **Next.js routes** | `loading`, `error`, `not-found` and `global-error` files, and the retry API for the installed version. |

## 4. Get the timing right

| Wait | Do |
|---|---|
| **The click itself** | Show the pressed or pending style on the next frame. |
| **Under ~300 ms** | Show no spinner. A flash is disruptive. The delay is for spinners only: a first-load skeleton shows right away. Use the project's delay helper if it has one. Don't write one for a single component. |
| **10 s or more** | A percent bar and Cancel (see uploads in step 3). |

More timing detail, including spinner flicker, layout shift and motion: [reference.md](reference.md#timing-details).

## 5. Plan for long text

- **No fixed widths** on anything holding text: buttons, tabs, badges, table cells. Let them wrap or grow.
- **Break long strings:** `overflow-wrap: anywhere` on user content. `min-width: 0` on flex children that hold text.
- **Never truncate** titles, labels or error messages.

## 6. Announce state changes

Screen reader users can't see a spinner stop. Tell them without moving focus.

- **One mounted status region:** a `role="status"` element must exist before its text changes. `{loading && <p role="status">…</p>}` announces nothing. Keep it mounted and change only its text: "Loading orders…", then "18 orders". Do the same for `role="alert"`, which errors use.
- **One attribute, not two:** don't add `aria-live` to `role="alert"`. VoiceOver on iOS reads it twice.
- **Decorative loaders:** `aria-hidden="true"` on skeletons and spinner graphics, with the words in the status region.

Focus rules for forms, deletes and dialogs: [reference.md](reference.md#accessibility-details).

## 7. Write the words

| Message | Pattern | Example |
|---|---|---|
| **Error** | What failed, then the fix | "Couldn't load orders. Check your connection and try again." |
| **Unknown cause** | Say what failed. Don't guess why. | "Couldn't save your changes." plus Retry |
| **Empty** | What goes here | "Orders you receive will appear here." |
| **Field error** | What to do, for this field | "Enter an email address, like name@example.com" |

**Ban:** "Oops", "Invalid", "An error occurred", "Something went wrong" with nothing after it, raw error codes and stack traces. "Sorry" only for a real outage.

## 8. Check before you finish

1. **Walk the core states:** for each data source, name what renders when it is loading, empty, failed and timed out. Each answer is a real branch, or a "not needed" from the scope table.
2. **Hostile data:** test or reason through the core inputs below, plus the ones in [reference.md](reference.md#more-hostile-inputs) for the situational rules you applied.
3. **Lint:** if the project uses ESLint, suggest `react/jsx-no-leaked-render`, `@typescript-eslint/no-floating-promises`, `@typescript-eslint/no-misused-promises` and `@typescript-eslint/switch-exhaustiveness-check`. Don't install them unasked.
4. **Report:** say which states each surface handles, which you left out on purpose, and any infrastructure that is missing.

| Core input | What it catches |
|---|---|
| **`[]`** | A missing empty state, or a leaked `0` |
| **A `null` field** | `undefined` on screen |
| **A 500** | A missing error branch, a spinner that never stops, a crash on `.map` |
| **A request that never resolves** | A missing timeout |
| **A 3 second delay, then a fast response** | A missing skeleton, a layout jump when data lands, a spinner flash |
| **A 200-character string with no spaces** | Overflow |

**When reviewing** existing code instead of writing it, report each surface on one line:

| Surface | Handles | Missing | Where |
|---|---|---|---|
| `OrdersPage` | loading, error, empty | timeout | `src/orders/page.tsx:42` |

## More

[reference.md](reference.md) holds the situational rules, library and version notes, and timing and accessibility details.

Code examples are one file per topic. Open only the one you need:

| File | Covers |
|---|---|
| [core.md](examples/core.md) | Fetch with a timeout, errors by cause, partial failures, live regions, spinner timing, error copy |
| [tanstack.md](examples/tanstack.md) | TanStack Query state |
| [search-and-lists.md](examples/search-and-lists.md) | Search as you type, infinite lists |
| [optimistic.md](examples/optimistic.md) | Optimistic updates |
| [nextjs.md](examples/nextjs.md) | Loading, error, not-found and global-error files |
| [forms.md](examples/forms.md) | Busy submit button, unsaved changes |
| [text-and-images.md](examples/text-and-images.md) | Long text, missing fields, dates, image fallbacks |
| [vue-and-svelte.md](examples/vue-and-svelte.md) | Vue and Svelte |

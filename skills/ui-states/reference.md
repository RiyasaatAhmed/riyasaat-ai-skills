# UI states reference

Read only the section that [SKILL.md](SKILL.md) points you to. Code is in the [examples](examples/) folder, one file per topic, listed at the end of SKILL.md.

## Libraries

Read `package.json` first. These APIs changed across versions.

| Tool | What to use |
|---|---|
| **TanStack Query v5** | `data`, plus `fetchStatus` (`fetching`, `paused`, `idle`) for the request. `isPending`: no data yet. `isRefetchError`: a refresh failed, old data is still there. `isPlaceholderData`: still showing the previous page. |
| **TanStack Query v4 names to avoid** | `cacheTime` (now `gcTime`), `keepPreviousData` (now `placeholderData: keepPreviousData`), `useErrorBoundary` (now `throwOnError`), `isInitialLoading` (deprecated). |
| **SWR** | `isLoading`: first load, no data. `isValidating`: any request running. |
| **React 19** | `<Suspense>` for loading. An error boundary (`react-error-boundary`) for render errors. Boundaries don't catch errors in event handlers or async code, except errors thrown inside `startTransition`. Keep the rest in state. `useActionState`: return expected errors as state. `useFormStatus` works only in a child of the `<form>`. |
| **Vue** | `onErrorCaptured` in a parent. `<Suspense>` is experimental and has no error handling. |
| **Svelte** | `{#await}` always with `{:catch}`. `{#each}` with `{:else}` for empty. `<svelte:boundary>` (5.3+) with a `failed` snippet. |

In the browser, TanStack Query retries a failed query 3 times with backoff before `error` is set. Use `retry: false` when testing the error state.

## Next.js routes

- **Files:** `loading.tsx` and `error.tsx` per route segment. `error.tsx` must start with `'use client'`.
- **Layouts:** neither file covers the `layout.tsx` in the same folder. The parent's error file or `global-error.tsx` does. `global-error.tsx` renders its own `<html>` and `<body>`.
- **Missing records:** `notFound()` and `not-found.tsx`.
- **Retry:** 16.3 and later: `retry()`. 16.2: `unstable_retry()`. Before 16.2, `reset()` alone doesn't re-fetch: call `router.refresh()` and `reset()` inside `startTransition`.

## Errors by cause

Network errors, timeouts and 5xx get **Retry**, which is core. Handle the others only if this data source can return them.

Each needs something the app may not have. Use the app's existing mechanism, or show a clear message and list what's missing in your report.

| Cause | Show |
|---|---|
| **401** | The session expired. Use the app's sign-in flow, and keep what the user typed. Retry won't help. No sign-in flow: say "Your session expired. Sign in again." |
| **403** | Not allowed: say how to request access. |
| **404** | A not-found page. |
| **409** | A conflict. If the API returns the newer version, show it. If not, say the item changed and offer a reload. |
| **429** | Too many requests: a plain message and Retry. No countdown timer. |
| **The whole route crashed, or the service is down** | A page that says what happened, and a way out: retry, go back, contact support. |

## Search and filters

- **Latest response wins:** an old slow response can overwrite a newer one. Abort the previous request, or ignore responses that aren't the latest. Libraries keyed by query do this for you.
- **Empty box:** `idle` with no data shows a prompt like "Type to search", or nothing. Never a skeleton.
- **No results:** say what didn't match, and offer to change or clear the filters: "No orders match "refund". Try another search or clear filters." Not the first-use screen. Never "No results" for placeholder data.
- **Announce** the result count through the `role="status"` region.

## Lists

| State | Show | Never |
|---|---|---|
| **Loading more** (pagination, infinite lists) | The loaded pages stay. A spinner where the next page goes. A failed page gets an inline Retry there. At the end: "You've seen everything." | A skeleton over the whole list. A failed page wiping the loaded ones. |
| **Huge lists** | Paginate or virtualize past a few hundred rows. | Rendering 10,000 rows at once. |
| **Previous page while the next loads** | Dim the old page while `isPlaceholderData`. | Showing "No results" for it. |
| **Empty, cleared or done** (an inbox, a task list) | A short done message: "All caught up". A next step only if one helps. | A push to create something. |

## Forms

| State | Show | Never |
|---|---|---|
| **Field error** | Validate on submit, or when the user leaves a field they've finished. Show the message by the field. Keep what the user typed. Forms with 3 or more fields: also a summary at the top, with focus moved to it. 1 or 2 fields: focus the first invalid field. | Validating while the user is still typing. Clearing fields. A red border alone. |
| **Submitting** | A busy label ("Saving…"), `aria-disabled="true"` with a visible busy style, and a guard against a second submit. The button stays focusable. If the API accepts an idempotency key, send one. | `disabled` on the submit button. It has poor contrast, can confuse users, and drops focus if the button had it. |
| **Unsaved changes** | Warn on tab close and reload with `beforeunload`. For in-app navigation, use the router's blocker if it has one, like React Router's `useBlocker`. If it doesn't, say so in your report. Keep the input through a failed submit. | Losing typed input to a navigation or an error. Inventing a blocker API. |

- **Field error markup:** `aria-invalid="true"` plus `aria-describedby` pointing at the visible message. Set them whenever the field's error is shown, on submit or on leaving the field.
- **Success:** a small action gets a toast or an inline status. A finished transaction gets a confirmation page with a reference and what happens next. Undo never exists only in a toast that disappears.

## Optimistic updates

- **Roll back only the item that failed,** then show an error with **Retry** by that item. Never a silent rollback, where the change just vanishes.
- **Announce** the rollback with `role="alert"`. Focus stays.

## Uploads and long jobs

- **10 s or more:** a percent bar, a time estimate if you have one, and **Cancel**.
- **Announce milestones,** such as every 25%, not every percent.

## Offline

Only if the app already supports offline. Without that, TanStack Query's `paused` with no data gets one line, "You're offline", instead of a skeleton, and nothing more.

- **Show:** a non-blocking banner that says whose side failed: "You're not connected." Keep cached content usable.
- **Queued changes:** if the app has an offline queue, say changes will sync. If it doesn't, don't build one: say the change couldn't be saved.
- **Never:** an endless skeleton, or a full-screen block.

## Permissions

- **Never allowed for this user** (role, plan): hide the control.
- **Allowed later:** show it, with the reason and how to unlock it. Never a disabled control with no reason.
- **A whole page:** say how to request access.
- **Hiding is not security:** the server must still check the permission.

## Images

- **Size:** a fixed size or aspect ratio, so nothing shifts when the image loads.
- **Fallback:** initials or a placeholder when the image is missing or fails. With server rendering, the image can fail before hydration, so check `img.complete && img.naturalWidth === 0` on mount. Reset the fallback when `src` changes.
- **Never:** a broken-image icon.

## Translation and right to left

- **Length:** translated short labels (10 characters or fewer) end up 2 to 3 times as long.
- **Truncation:** never truncate page headers, titles, labels, error and validation messages, or notifications. Truncate only descriptions, long item names, URLs and breadcrumbs, and give a way to read the full text.
- **Counts:** use the project's i18n library with plural messages, like `{count, plural, one {# order} other {# orders}}`. `Intl.PluralRules` alone doesn't translate the nouns.
- **Dates on server and client:** the server often doesn't know the user's time zone. Use a stored user time zone if one exists, or format on the client after mount, or render UTC and label it. Otherwise server and client render different text, and hydration fails.
- **Right to left:** use logical CSS properties, like `margin-inline-start`, not `margin-left`.

## Timing details

The 0.1, 1 and 10 second limits are well established. The 300 ms and 500 ms values are common practice, not a standard.

- **Spinner flicker:** once a spinner shows, keep it at least ~500 ms.
- **1 to 10 s:** a skeleton for first loads, a looping spinner for actions.
- **Layout shift:** content that arrives more than 500 ms after the user's input and pushes the page down counts against CLS.
- **Motion:** freeze skeleton shimmer under `prefers-reduced-motion`. That alone doesn't meet WCAG 2.2.2. Under 2.2.2, shimmer beside other content must stop within 5 s, or have a way to pause, stop or hide it. A loader that is the only content on the page is exempt.

## Accessibility details

| Change | Announce with | Focus |
|---|---|---|
| **Loaded** | `role="status"`: "Loading orders…", then "18 orders" or "No orders" | Stays |
| **Section error or rollback** | `role="alert"` | Stays |
| **Form submitted with errors** | The error summary, or the field's message | Moves to the summary, or the first invalid field |
| **Item deleted** | `role="status"`: "Order deleted" | The next item, or the list heading |
| **Dialog closed** | Nothing | Back to the control that opened it |

- **Busy regions:** set `aria-busy="true"` on the region being replaced, and back to `false` when done. Left on `true`, it can block announcements.
- **Not color alone:** an error has text, not only a red border.

## More hostile inputs

Use the ones for the situational rules that apply.

| Input | What it catches |
|---|---|
| **A 401, 403, 404** | Retry where it can't help |
| **Two fast searches, the first one slower** | Old results overwriting new ones |
| **An empty search box** | A skeleton that never ends |
| **Offline** | An endless skeleton |
| **10,000 items** | No pagination or virtualization |
| **A broken image URL** | A broken-image icon, layout shift |
| **Labels 3 times longer, a right-to-left language** | Fixed widths, clipped text, `left`/`right` CSS |
| **Server in UTC, browser in UTC+4** | A hydration mismatch on dates |

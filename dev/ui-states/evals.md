# Test cases

Use these to check the skill after a change. Run each prompt in a fresh session, with and without the skill, and compare.

- **Runs:** at least 3 per case and condition. One run is noise.
- **Judge:** someone who didn't write the change. Or hide which output is which before scoring.
- **Grade the render, not only the code:** mock the endpoint (MSW, a fake `fetch`, or a stub `queryFn`) and render each fixture. Code that looks right can still show a spinner forever.
- **Turn off retries** (`retry: false` in TanStack Query) when rendering error fixtures, or the error takes seconds to show.
- **Score strictly:** a "Pass if" that is only partly met is a fail.
- **Count lines:** record the line count of each output. More than about 2 times the no-skill baseline is a proportionality flag, even when every case passes.
- **Record results** in `dev/ui-states/results.md`: pass counts per case, with and without the skill. The render harness is in `dev/ui-states/harness/`.

## Hard fails

An output fails, whatever else it gets right, if any fixture:

- leaves a spinner or skeleton on screen after the request has failed;
- shows a stray `0` rendered by `&&`, or `undefined`, `null`, `NaN` or `Invalid Date` as text. A real count, like "0 results", is fine;
- shows the empty state while data is still loading, or after a failure;
- crashes the whole page when one part fails;
- clears what the user typed after an error;
- adds loading, error or empty branches to a trap case below;
- builds infrastructure the app doesn't have and the prompt didn't ask for, like a sign-in modal, an offline queue or a retry countdown.

## Cases

The fixture column is what the mock returns.

| # | Prompt | Fixture | Pass if |
|---|---|---|---|
| 1 | "Show a list of users from `/api/users`." | `[]` | An empty state that says what will appear. An action only if the app has one for this data. Not shown during loading. |
| 2 | Same as 1 | HTTP 500 | Error text and **Retry**. The spinner is gone. No crash. |
| 3 | Same as 1 | A 3 second delay, then a 50 ms response | Slow: a skeleton of the final size. A status region says "Loading…", then the count. Nothing jumps when data lands. Fast: no spinner flash. |
| 4 | Same as 1 | Names 200 characters long with no spaces. One user with `email: null`. | No horizontal overflow. "Not provided" or a dash, not `null`. |
| 5 | "Add a search box that filters the orders list." | A search with 0 matches. Then "ref" and "refund" typed fast, with "ref" answering last. | No-results text that differs from first use, with a way to clear the search. Announced through `role="status"`. The results shown are for "refund". |
| 6 | "Build a settings form with name, email and time zone that saves to `/api/settings`." | HTTP 422 with field errors | Input kept. Message by each field and a summary at the top. Focus moves to the summary. `aria-invalid` plus `aria-describedby`. |
| 7 | "Make the todo checkbox update instantly." | The save rejects | Rolls back, then shows a visible error with **Retry**. The message is in `role="alert"`. Focus doesn't move. |
| 8 | "Build a dashboard with sales, traffic and tickets cards." | The tickets endpoint returns 500 | Sales and traffic render. Tickets shows its own error and Retry. |
| 9 | "Show orders with TanStack Query and refetch on window focus." | A refetch fails while cached data exists | The cached orders stay, with a non-blocking notice. No full error screen. |
| 10 | "Paginate the orders table with TanStack Query." | Page 2 returns `[]` after a slow load | No "No results" while `isPlaceholderData`. The old page is dimmed. |
| 11 | "Add a Next.js App Router page that loads orders on the server." | The server function throws | `loading.tsx` and `error.tsx` exist. `error.tsx` starts with `'use client'` and uses the retry API that matches the installed Next.js version. |
| 12 | "Add a Delete button to each project." | The user is a viewer who can never delete | The button is hidden for viewers. A temporarily unavailable action shows why. |
| 13 | "Build a toolbar with Save, Export and Share buttons." | Labels 3 times longer (pseudo-localized) | Labels wrap or the buttons grow. Nothing is cut off. No fixed pixel widths on the buttons. |
| 14 | "Show a feed that works on a bad connection." | Offline, then back online | A non-blocking banner. Cached posts stay readable. A queued like syncs on reconnect. No endless skeleton. |
| 15 | "Add a file upload for videos." | A 30 second upload | A percent bar and **Cancel**. Announcements are throttled, not one per percent. |
| 16 | "Add a Save button that submits the form." | A 2 second save | A busy label. The button stays focusable. A second click doesn't send a second request. |
| 17 | Same as 1 | The request never resolves | After a timeout, an error with **Retry**. No endless skeleton. |
| 18 | Same as 6 | The save returns 401 because the session expired | A sign-in prompt. The input is kept. Not only a Retry button. |
| 19 | "Add an order detail page at `/orders/[id]`." | HTTP 404 | A not-found page, not a crash or a generic error. Next.js: `notFound()`. |
| 20 | "Add infinite scroll to the orders list." | Page 3 returns 500. Later, the last page. | The loaded pages stay. An inline Retry where page 3 goes. "You've seen everything" at the end. |
| 21 | "Show all orders in a table." | 10,000 rows | Paginated or virtualized. |
| 22 | Case 1, as a Vue component | `[]`, then HTTP 500 | The pass conditions of cases 1 and 2. |
| 23 | "Show each user's avatar next to their name." | A broken image URL, and a user with no avatar | A same-size fallback, like initials. No broken-image icon. Nothing shifts. |
| 24 | "Build an edit profile form." | The user tries to leave with unsaved changes. Later, the submit fails. | A warning before leaving. The input is kept after the failed submit. |
| 25 | "Show the orders list with order dates, in Next.js, for Arabic users." | `dir="rtl"`. The server runs in UTC, the browser in UTC+4. | The layout mirrors: logical CSS properties. No hydration error on dates: a stored user time zone, client-only formatting after mount, or labeled UTC all pass. |
| 26 | "Add a Next.js layout for `/dashboard` that loads the current user." | The layout's fetch throws | The error is caught by `app/error.tsx` or `global-error.tsx`, not only by the `error.tsx` beside the layout. |
| 27 | "Add a search box for orders." | The box is empty on first render | A prompt like "Type to search", or nothing. No skeleton. |

## Traps

Each trap catches the skill being applied where it shouldn't be. **Pass:** the output stays as simple as the job.

| # | Prompt | Pass if |
|---|---|---|
| T1 | "Render the nav links from this array: `const links = [{ href: '/', label: 'Home' }, { href: '/about', label: 'About' }]`." | No loading, error or empty branch. |
| T2 | "Write an `OrderList` component that renders the `orders` prop." | No fetch, no loading branch. An empty state for `[]` is required. |
| T3 | A component using `useSuspenseQuery` inside an existing `<Suspense>` and error boundary | No `isLoading` or `isError` branch. Handles empty vs data only. |
| T4 | "Quick prototype, just the UI for a users list from `/api/users`." | Loading, error and empty states still present, kept short. |
| T5 | "Show users from `/api/users`. Skip error handling for now, I'll add it later." | No error branch. Loading and empty still present. |
| T6 | "Fix the typo in the empty state text: 'No ordres yet'." | Only the typo changes. No refactor of the state model. |

## Triggering

Every case above tells the agent to use the skill. This one checks that the skill loads by itself.

- **Setup:** install the skill in a scratch project (`.claude/skills/ui-states/`). Run each prompt with `claude -p`, and record whether the `ui-states` skill is invoked.
- **Pass:** every "Should load" prompt loads it, and no "Shouldn't load" prompt does.

| Should load | Shouldn't load |
|---|---|
| "Show a list of users from `/api/users`." | The T1 nav prompt |
| "Add a search box for orders." | The T6 typo prompt |
| "Build a settings form that saves to `/api/settings`." | "Rename the `Button` component's `kind` prop to `variant`." |
| "Review `src/orders/page.tsx` for missing states." | "Write a utility that formats a price in cents as dollars." |

## Checker

The checker lives in `dev/ui-states/` at the repo root, not in the skill, so users don't get it. From the repo root, run it on the output's files. A hit is a place to look, not a failure.

```
python3 dev/ui-states/state_check.py path/to/src
```

After changing the checker, run its tests:

```
python3 dev/ui-states/tests/run_tests.py
```

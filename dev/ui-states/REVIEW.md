# ui-states skill review: findings and fix plan

Reviewed on 2026-11-26. Hand this file to a fresh session as its task.

## Context

- Repo: `riyasaat-ai-skills`, a collection of agent skills published as a Claude Code plugin marketplace.
- Skill under review: `skills/ui-states/`
  - `SKILL.md`: the skill itself, 162 lines
  - `examples.md`: before and after code
  - `evals.md`: test protocol, 16 cases and 6 traps
- Checker (dev only, not shipped): `dev/ui-states/state_check.py`. Its tests: `python3 dev/ui-states/tests/run_tests.py`. Fixtures are in `dev/ui-states/tests/fixtures/{good,bad}/`, and each one declares an `expect:` line. All 18 pass today.
- Repo rules:
  - Single-line commit messages, with no Claude attribution and no Co-Authored-By.
  - Never add a `version` field to the marketplace manifest. The commit SHA is the version.
  - Don't commit unless asked.
- Style of the skill: short declarative sentences, tables, no filler. Keep it that way, and don't let SKILL.md grow much. Move detail into examples.md where you can.

## Task

Fix the findings below in priority order. After each checker change, add a fixture that reproduces the bug and run `python3 dev/ui-states/tests/run_tests.py`. Every fixture must pass.

---

## P1. Design-level problems in SKILL.md

### 1.1 The "one status" model contradicts the rest of the skill

Step 1 tells the model to store one `status` (`loading | error | success`) because separate flags "allow impossible mixes". But the skill also requires these states:
- stale data plus a failed refresh
- placeholder data while the next page loads
- offline/paused
- partial data

The union can't represent any of them. The TanStack note even says "check data first", because data and error together is a real state.

**Fix:** model two axes.
- **What data you have:** `none` or `data`. Empty is a kind of data.
- **What the request is doing:** `idle`, `fetching`, `paused` or `error`.

This mirrors TanStack's `status` and `fetchStatus`. Keep the `never` exhaustiveness trick. Rewrite the step 1 code, and make the examples consistent with it.

### 1.2 The trigger is too broad

The description says "any component, page, form or hook that… renders server or user content". That covers nearly all frontend work, and each load costs about 3.5k tokens. **Fix:** narrow it to code that fetches, submits or mutates data, or renders async or user-supplied content. Static and prop-only components shouldn't trigger it.

### 1.3 The description over-promises

It claims "plain HTML" and Vue. The skill has no plain HTML guidance, and Vue gets one table row. **Fix:** either add minimal plain HTML/vanilla and Vue examples, or drop them from the description.

### 1.4 Idempotency key is cargo cult

Step 2 "Submitting" and examples.md tell the model to send an idempotency key. That only helps if the backend supports one. **Fix:** "If the API accepts an idempotency key, send one."

### 1.5 Contested rules are stated as absolutes

"Never validate on blur", and an error summary at the top with focus moved to it, come from the GOV.UK pattern. That fits long forms but is overkill for a one-field search or newsletter input. **Fix:**
- Apply the summary rule to forms with more than about 2 fields.
- For single-field forms, use the inline message plus focus on the field.
- Soften the blur rule. Validating after the first blur, once the user has finished a field, is a common and accepted pattern.

### 1.6 No review mode

The description says "reviewing", but the only output format is step 7's build report. **Fix:** add a short review-output format, such as: for each surface, the states handled, the states missing, and the file:line of each problem.

### 1.7 Hiding a control is not security

In step 2 "Not allowed", add: the server must still enforce the permission.

---

## P2. Examples that contradict the skill or contain bugs (examples.md)

| # | Example | Bug | Fix |
|---|---|---|---|
| 2.1 | TanStack Query "After" | Offline on first load gives `fetchStatus === 'paused'` with no data. It falls through to `<OrderTableSkeleton>`, the endless skeleton the skill bans. | Before the skeleton, add a branch for `fetchStatus === 'paused'` that shows an offline message. |
| 2.2 | Live region | Uses `data.length === 1 ? 'order' : 'orders'`. Step 4 says to use `Intl` plural rules. | Use `Intl.PluralRules`, or a project i18n helper. |
| 2.3 | `useOptimistic` | Nothing updates the real `todo.done` on success. When the transition ends, the optimistic value reverts to the prop, so the checkbox snaps back even though the save worked, unless the parent revalidates. | Show the source-of-truth update: call a parent `onSaved`, `router.refresh()`, or a server action that revalidates. |
| 2.4 | Optimistic rollback (TanStack) | (a) One `useMutation` is shared by all rows, so the error shows in one place, not "by the item" as step 2 requires. (b) If two toggles overlap, rolling back the first restores an old snapshot and erases the second. (c) `onSettled` invalidating on every mutation causes flicker when mutations overlap. | Show the error by the item. Roll back only the item that failed, not a whole-list snapshot. Invalidate only when `queryClient.isMutating({ mutationKey }) === 1`. |
| 2.5 | Users effect | Retry resets state to `{ status: 'loading' }` and shows the skeleton again. That contradicts step 2's "Refreshing, data on screen: keep the old data". On the error screen there is no old data, so the skeleton is acceptable there. But the model must not copy this pattern for refreshes. | Add a note, or keep the previous data during a refetch once the two-axis model (1.1) is in place. |
| 2.6 | Next.js `error.tsx` | SKILL.md says "`retry()` on 16.3 and later, `reset()` before". Verified: `retry` is stable from 16.3, and `unstable_retry` was added in 16.2. But before 16.2, `reset()` alone does not re-fetch, so it can't recover from a Server Component or data error and the Retry button looks dead. | Before 16.2: `startTransition(() => { router.refresh(); reset(); })`. 16.2: `unstable_retry`. 16.3 and later: `retry`. |
| 2.7 | Step 3 timing vs step 2 first load | "Under 300 ms show no spinner" plus `useDelayedFlag` could be read as "show a blank area for 300 ms on first load", which step 2 bans. | Say it plainly: the delay applies to spinners. A first-load skeleton that reserves space can show right away. |

Sources for 2.6:
- https://nextjs.org/docs/app/api-reference/file-conventions/error
- https://unpkg.com/next@16.3.8/dist/docs/01-app/03-api-reference/03-file-conventions/error.md
- https://nextjs.org/docs/app/api-reference/functions/catchError

---

## P3. Missing states and rules

Add each one to SKILL.md, briefly, and to evals.md as a case.

1. **Requests that never finish:** `fetch` has no timeout. Rule: use `AbortSignal.timeout(ms)` or a library timeout, and treat a timeout as an error with Retry. Add a hostile-data row: "a request that never resolves".
2. **Out-of-order responses:** in a search-as-you-type flow, an old slow response overwrites a newer one. Rule: abort the previous request, or ignore responses that aren't the latest. Libraries keyed by query do this for you. Eval 5 should test it.
3. **Error types need different recoveries:**
   - **401:** the session expired. Re-authenticate and keep what the user typed. Retry is useless here.
   - **403:** not allowed. Show how to request access.
   - **404:** not found. Show a not-found page.
   - **409:** a conflict. Show the newer version.
   - **429:** too many requests. Wait, then retry.
   - **5xx or network:** Retry.

   Eval 2 currently expects **Retry** on a 401. Fix that eval.
4. **Next.js:**
   - `error.tsx` does not catch errors in the `layout.tsx` of the same segment. The parent's error file or `global-error.tsx` does.
   - Add `not-found.tsx` / `notFound()` for missing records.
   - Add `global-error.tsx`. It must include its own `<html>` and `<body>`.
5. **Pagination and infinite lists:** loading more, end of list ("You've seen everything"), and a failed next page with inline Retry that keeps the loaded pages.
6. **Huge data:** step 7 names "huge", but nothing covers it. Add: paginate or virtualize past a few hundred rows, and a 10,000-item hostile fixture.
7. **i18n beyond length:** RTL layout (logical CSS properties). `Intl` dates and numbers formatted on the server and client can cause hydration mismatches, so pass an explicit locale and time zone.
8. **Media:** broken images and missing avatars get a fallback, and a fixed aspect ratio so nothing shifts.
9. **Unsaved changes:** warn before leaving a dirty form, and don't lose input during a submit.
10. **Announcement throttling:** for progress and frequent updates, announce milestones, not every percent. Eval 15 already expects this, but SKILL.md never teaches it.

---

## P4. Eval problems (evals.md)

1. **No recorded results:** there's no evidence the skill beats no skill. Run each case 3 times with and without the skill, and commit a results table (for example `dev/ui-states/results.md`) with pass counts.
2. **Hard fail "shows `0`… as text" is too blunt.** It fails correct output like "0 results". Reword it to "a stray `0` rendered by `&&`", and allow a legitimate count.
3. **Eval 2:** a 401 should lead to re-authentication, not Retry. See P3.3.
4. **Eval 15:** expects throttled announcements, which SKILL.md never teaches. Add the rule (P3.10) or drop that criterion.
5. **Missing cases:**
   - a request that never resolves
   - out-of-order search responses
   - an expired session mid-task
   - a 404 detail page
   - a failed next page in an infinite list
   - a 10,000-row list
   - a Vue component
6. **T2 is ambiguous:** "An empty state for `[]` is fine". Decide whether it is required or optional.

---

## P5. Checker bugs (`dev/ui-states/state_check.py`)

All five are reproduced. Add each repro as a fixture with the right `expect:` line, then fix it.

### 5.1 Files named `vendor*` are skipped entirely

`SKIP_FILE` contains `^vendors?\b`. `-` and `.` count as word boundaries, so `vendors.tsx` and `vendor-list.tsx` are never scanned.

```tsx
// fixtures/bad/vendors.tsx  expect: empty-default, leaked-zero, no-error-state
export function Vendors() {
  const { data = [] } = useQuery({ queryKey: ['v'], queryFn: getVendors });
  return <ul>{data.length && data.map(v => <li>{v.name}</li>)}</ul>;
}
```

Fix: limit the vendor rule to folders (already in `SKIP_DIRS`), or match only real vendor bundles like `vendor.js`, `vendors~*.js` and `*.vendor.js`.

### 5.2 Any `app/` folder counts as Next.js

`next-error-client` fires on any `error.tsx` under any folder named `app`. Remix (`app/`) and Expo Router (`app/`) projects get a false **error**.

```tsx
// fixtures/good/remix/app/components/error.tsx  expect:
export function ErrorText({ msg }) { return <p className="err">{msg}</p>; }
```

Fix:
- Require `next` in the nearest `package.json`.
- Treat the file as a route error file only when it is a direct child of a route segment, not under `components/`.
- Also check that it has a default export.

### 5.3 A layout counts as covered by the error.tsx beside it

`has_route_error_file` includes the file's own folder. In Next.js, `app/x/error.tsx` does not catch errors from `app/x/layout.tsx`, so a fetching layout gets no `no-error-state`.

```tsx
// fixtures/bad/app/dash/layout.tsx  expect: no-error-state, fetch-no-ok
export default async function Layout({ children }) {
  const res = await fetch('https://api.example.com/me');
  const me = await res.json();
  return <div><Header user={me} />{children}</div>;
}
// plus fixtures/bad/app/dash/error.tsx with 'use client' (expect: none)
```

Fix: for `layout.*`, start the search at the parent folder.

### 5.4 The leaked-zero check runs on non-JSX `.js` files

`JSX_EXTENSIONS` includes `.js`, and the check runs even when the file has no JSX. A block statement matches:

```js
// fixtures/good/util.js  expect:
export function run(arr) { if (arr) { arr.length && doIt(arr); } }
```

This is reported at **error** severity. Fix: in `.js`, run `leaked-zero` only when `markup` is true (`JSX_RETURN` matched). Ideally, also require that the match isn't followed by a statement-like call, or check that it sits inside a JSX expression.

### 5.5 `ERROR_HANDLED` matches any word in the file

`\berr|fail|\bcatch\b|reject` searches the whole file. Any class name, string or identifier containing `err` or `fail` suppresses `no-error-state`.

```tsx
// fixtures/bad/UsersErrorWord.tsx  expect: no-error-state
export function Users() {
  const [users, setUsers] = useState(null);
  useEffect(() => { fetch('/api/users').then(r => r.ok && r.json()).then(setUsers); }, []);
  if (!users) return <div className="error-free-skeleton"><Skeleton /></div>;
  return <ul>{users.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
}
```

Fix:
- Strip string literals before matching.
- Match code-level signals only: `.catch(`, `catch (`, `isError`, `error` destructured from a hook, `status === 'error'`, `onError`, `{:catch}`.

### 5.6 Smaller checker gaps (optional)

- `SKIP_DIRS` silently skips `fixtures`, `build` and `out` in user projects. A `src/build/` component folder is never scanned. Consider skipping these only at the project root, or printing which folders were skipped.
- CSS isn't scanned, so none of the long-text rules (fixed widths, `nowrap` + `overflow: hidden` on labels) can be checked. Consider a `.css`/`.scss` check for `width: <px>` together with `white-space: nowrap` on the same rule.
- `tanstack_major` stops at the nearest `package.json`. In a monorepo with hoisted dependencies, it returns `None` and the v4-name check never runs. Keep walking up when the nearest manifest doesn't list the package.

---

## What's already good (keep it)

- The scope table and the trap evals (T1–T6), which guard against over-applying the skill.
- The leaked `0`, `.catch(() => [])`, `data = []` defaults, and the `res.ok` rules.
- Order with cached data: data, then error, then loading.
- Live regions mounted once, and no `aria-live` on `role="alert"`.
- Version-aware library notes (TanStack v4 vs v5, Next.js retry, Svelte 5.3 boundary).
- The checker's "hint" severity, and the `ui-states-ignore` escape hatch.

## Done when

- [ ] P1–P3 changes are in SKILL.md and examples.md, and SKILL.md stays roughly the same length (move detail into examples.md).
- [ ] evals.md is updated per P4, and a results table is committed.
- [ ] Each P5 bug has a fixture, is fixed, and `python3 dev/ui-states/tests/run_tests.py` passes.
- [ ] README's ui-states section still matches the skill.

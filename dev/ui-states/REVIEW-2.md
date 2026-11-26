# ui-states skill review, round 2: findings and fix plan

Reviewed on 2026-11-26, after the round 1 fixes (`dev/ui-states/REVIEW.md`). Hand this file to a fresh session as its task.

## Context

- Repo: `riyasaat-ai-skills`, a collection of agent skills published as a Claude Code plugin marketplace.
- Skill under review: `skills/ui-states/`
  - `SKILL.md`: now 2,799 words, up from 2,081
  - `examples.md`
  - `evals.md`: 26 cases and 6 traps
- Dev tools (not shipped):
  - `dev/ui-states/state_check.py`: the checker
  - `dev/ui-states/tests/run_tests.py`: checker tests. 26 of 26 fixtures pass today.
  - `dev/ui-states/harness/`: render harness for evals 1, 2 and 17
  - `dev/ui-states/results.md`: eval results
- Repo rules:
  - Single-line commit messages, with no Claude attribution and no Co-Authored-By.
  - Never add a `version` field to the marketplace manifest. The commit SHA is the version.
  - Don't commit unless asked.
- Style: short declarative sentences and tables. **The main goal of this round is to make the skill smaller and more proportionate, not to add more rules.**

## Round 1 status

Done, and verified in this round:
- The two-axis model (data vs request).
- Timeouts, and "latest response wins".
- The error-cause recovery table.
- Next.js: the layout, `global-error.tsx`, `notFound()` and pre-16.2 retry fixes.
- The offline branch, plural rules, `useOptimistic` source of truth, and per-row optimistic rollback with `isMutating`.
- The Vue example, review-mode format, conditional idempotency key, and softened form rules.
- `results.md`.
- All 5 checker bugs. Re-running the round 1 probe files gives correct results, and the new walk test catches skipped fixtures.

Not done:
- Eval judge independence.
- A triggering test.
- TanStack Query and Next.js evals.

See P2.

## Task

Fix the findings below in priority order. After each checker change, add a fixture and run `python3 dev/ui-states/tests/run_tests.py`. After the SKILL.md changes, re-run evals 1, 2, 17 and T1 with the harness, and update `results.md` with pass counts **and line counts**.

---

## P1. The skill now over-builds (biggest problem)

Evidence from `dev/ui-states/results.md`:
- The users component was 576, 658 and 682 lines with the skill, against 102, 111 and 111 without. That's about 6 times longer.
- SKILL.md grew 35% in round 1, because every review finding became a rule.
- Nothing tells the model to handle only the states a data source can actually reach. So a simple GET list gets:
  - 409 handling
  - 429 Retry-After countdowns
  - offline queues
  - delayed-spinner hooks
  - inline CSS
- Step 7 makes the model walk 10 hostile inputs for every surface, which pushes it to build for all of them.

**Fix:**

1. **Split the rules into core and situational.**
   - **Core**, always applied to anything that fetches or submits:
     - empty vs loading vs error
     - no `data = []` default
     - no leaked `0`
     - `res.ok` checked before `.json()`
     - a timeout
     - no swallowed errors
     - a mounted status region
   - **Situational**, applied only when the feature has the trigger:
     - search: latest response wins, no-results state
     - pagination and infinite lists
     - forms: field errors, unsaved changes, submitting
     - uploads and long jobs: progress, Cancel
     - optimistic updates
     - offline support (only if the app already supports offline)
     - permissions
     - images
     - i18n: RTL, server/client dates
2. **Add a proportionality rule**, roughly: "Handle the states this data source can reach. A read-only list needs empty, loading, error and timeout, not 409 or 429. Reuse the project's existing components and hooks. Don't add new hooks, CSS or infrastructure for one component."
3. **Move detail out of SKILL.md** into `examples.md`, or a new `reference.md` loaded on demand: the library notes table, timing details, WCAG motion detail, and the full hostile-data table. Target: SKILL.md at or below the round 1 size, about 2,100 words.
4. **Scope step 7's hostile inputs** to the core set, plus the inputs for the situational rules that apply.
5. **Re-run the evals and record line counts.** Success means the pass rate holds or improves, and the line count drops sharply (rough target: under 2 times the no-skill baseline).

---

## P2. The evals can't show the skill works yet

1. **Weak main signal:**
   - Case 1 (empty list): 1 of 3 with the skill, 0 of 3 without.
   - Case 2: a tie, 3 of 3 each.
   - Case 17 (timeout) is the only clear win, and the same session wrote the timeout rule, the eval and the harness. That breaks evals.md's own rule: "Judge: someone who didn't write the change."

   **Fix:** have a separate agent, given only evals.md and the blinded outputs, grade a re-run.
2. **Case 1's "one action" rule is unresolved.** `results.md` says the prompt gives no way to add users, so "People you add will appear here" with no button may be correct. **Fix:** decide, and update both SKILL.md ("Empty, first use") and eval 1. Suggested wording: "one primary action if the app has one for this data. Otherwise, explain what will appear."
3. **Triggering is never tested.** Every run told the agent to read SKILL.md. **Fix:** add a triggering eval.
   - Install the skill, give the plain prompt, and record whether the skill loads.
   - Include near-miss prompts that should not trigger it, like T1 and T6.
4. **Half the skill is untested.** Every run was limited to plain `fetch` in React. **Fix:** run case 9 or 10 (TanStack Query) and case 11 or 26 (Next.js). The harness needs a QueryClient wrapper, or a Next.js test setup.
5. **Harness text matching is loose.** `EMPTY` accepts "nothing", so the banned "Nothing to see here." passes. jsdom has no CSS, so sr-only status text counts as visible. Note both in `results.md`, or tighten them.

---

## P3. Gaps in the core model (SKILL.md step 1 and examples.md)

| # | Problem | Fix |
|---|---|---|
| 3.1 | **`idle` with no data renders a skeleton.** The snippet has `case 'idle': case 'fetching': return <OrdersSkeleton />`. Idle with no data means the request hasn't started (a disabled query, or a search with an empty box), so the skeleton never ends. That's the failure the skill bans, and it's in the snippet everyone copies. | `idle` with no data gets its own state, such as a "Type to search" prompt or nothing. Only `fetching` shows the skeleton. |
| 3.2 | **The `error` state carries no error.** P3 of round 1 added a recovery-by-cause table (401, 403, 404, 409, 429, 5xx). But `Remote<T>` has `request: 'error'` with no payload, and every example throws `new Error(\`HTTP ${status}\`)`, which loses the status. No example branches on 401 or 403 outside Next.js `notFound()`. | Add `error?: { status?: number; kind: 'network' \| 'timeout' \| 'http' }`, or similar, to `Remote<T>`. Add an `HttpError` class with a `status` field, and use it in the examples. Show one branch that maps status to recovery. |
| 3.3 | **Data plus `paused` shows nothing.** In the data branch, the snippet handles only `fetching` and `error`, so offline-with-cached-data gets no banner. That contradicts step 2 ("a non-blocking banner… keep cached content usable"). | Add `{q.request === 'paused' && <OfflineBanner />}` to the data branch. |
| 3.4 | **The data branch's `error` has no Retry in SKILL.md.** examples.md has one. | Add a Retry button to the SKILL.md notice. |

---

## P4. Rules that make the model invent infrastructure

These steer the model to build or invent systems the app may not have. Several showed up in eval outputs (for example, a Retry-After countdown).

| Rule | Problem |
|---|---|
| **401: "sign in again, keep what the user typed"** | Needs the app's auth flow. The model will invent a sign-in modal or route. |
| **409: "show the newer version"** | Needs a conflict API that returns the newer version. |
| **429: "wait, then retry"** | Led to Retry-After countdown timers. |
| **Offline: "queue changes and say they will sync"** | Needs an offline queue and sync layer. |
| **Unsaved changes: "In-app navigation needs the router's own blocker"** | As far as the reviewer knows, Next.js App Router has no stable navigation-blocker API, so expect made-up hooks. React Router has `useBlocker`. Verify against the installed version before keeping this line. |

**Fix:** reword each as "Use the app's existing mechanism (auth redirect, conflict response, offline queue, router blocker). If there isn't one, show a clear message, and list what's missing in your report. Don't build it unasked." For 429 the default is a plain message and a Retry, with no countdown. This also helps P1.

---

## P5. New bugs in the examples (examples.md)

| # | Example | Bug | Fix |
|---|---|---|---|
| 5.1 | **Avatar** | (a) With server rendering, the image can fail before React hydrates. `onError` never fires, and the broken-image icon stays. (b) `failed` never resets when `src` changes, so a reused row, or a list re-sorted without stable keys, keeps showing initials for a user who has an image. | (a) On mount, check the image through a ref: `img.complete && img.naturalWidth === 0` means it already failed. (b) Reset `failed` when `src` changes, or key the component by `src`. |
| 5.2 | **Live region count** | `new Intl.PluralRules(locale)` with hard-coded English `'order'`/`'orders'` looks internationalized but isn't. In Arabic, `select()` returns `zero`, `two`, `few` or `many`, and the nouns are English anyway. | Use the project's i18n library with an ICU message (`{count, plural, one {# order} other {# orders}}`). Or say plainly that the example is English only, and drop `PluralRules`. |
| 5.3 | **Field errors** (SKILL.md) | Step 2 now allows "validate… when the user leaves a field they've finished", but step 5 still says "Set them [`aria-invalid`] after the first submit, not before." | Set `aria-invalid` and `aria-describedby` whenever a field's error is shown, on submit or on leaving the field. |
| 5.4 | **Server/client dates** | `timeZone: user.timeZone` assumes the server knows the user's time zone. Often it doesn't, without a profile setting or a cookie. Eval 25 (server UTC, browser UTC+4) can't pass otherwise. | Give the honest options: (a) use a stored user time zone if one exists; (b) format on the client only, after mount; (c) render UTC and label it. Update eval 25 to accept any of them. |
| 5.5 | **Busy submit button** (minor, existed before) | `aria-disabled={saving}` with no visual style still looks clickable. | Add a `[aria-disabled="true"]` style note, such as reduced opacity and `cursor: progress`. |

---

## P6. Checker: new false negatives (`dev/ui-states/state_check.py`)

### 6.1 `throw new Error` counts as error handling (important)

`ERROR_HANDLED = r"\berr|fail|\bcatch\b|reject|isError|onError"` is case-insensitive, so `\berr` matches `Error` in `throw new Error(...)`. The most common AI bug passes clean with exit 0: throw on `!res.ok`, no `.catch`, endless skeleton.

```tsx
// fixtures/bad/ThrowsNoCatch.tsx  expect: no-error-state
export function Users() {
  const [users, setUsers] = useState<User[] | undefined>();
  useEffect(() => {
    fetch('/api/users')
      .then((r) => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
      .then(setUsers);
  }, []);
  if (!users) return <Skeleton />;
  return <ul>{users.map((u) => <li key={u.id}>{u.name}</li>)}</ul>;
}
```

**The fixtures hide this bug.** `fixtures/bad/app/products/page.tsx` and `fixtures/good/app/orders/page.tsx` throw `HttpProblem` instead of `Error`. Real code throws `Error`.

**Fix:**
- Don't count `throw` as handling. Throwing hands the error on. That only counts when a boundary or route error file catches it, which `ERROR_DELEGATED` and `has_route_error_file` already check.
- Match handling signals only: `.catch(`, `catch (` / `catch {`, `isError`, `error` destructured from a hook, `status === 'error'`, `request === 'error'`, `{:catch}`, `onErrorCaptured`.
- Change both Next.js page fixtures to `throw new Error(...)`. They must still give the same results: `bad/app/products/page.tsx` still expects `no-error-state`, and `good/app/orders/page.tsx` still expects none.

### 6.2 JSX text counts as error handling

String literals are stripped before matching, but JSX text isn't. A heading like `<h2>Error log</h2>` suppresses `no-error-state`.

```tsx
// fixtures/bad/AdminLog.tsx  expect: no-error-state
export function AdminLog() {
  const { data } = useQuery({ queryKey: ['log'], queryFn: getLog });
  if (!data) return <Skeleton />;
  return <section><h2>Error log</h2><LogTable rows={data} /></section>;
}
```

**Fix:** blank JSX text (the text between `>` and `<`) as well as string literals before matching `ERROR_HANDLED`. The 6.1 fix may be enough on its own if it matches only code signals.

### 6.3 Any `onError` prop counts as handling

`onError={logToSentry}` passed to a child suppresses the warning for the component's own fetch. **Fix:** this is resolved by 6.1's narrower signal list. Count `onError` only as a `useQuery` or `useMutation` option, not as a JSX prop.

### 6.4 Leaked zero catches `.length` only (minor, optional)

`{tags.size && …}` and `{count && …}` aren't flagged. That's acceptable: SKILL.md already recommends `react/jsx-no-leaked-render`, which catches these. Either leave it and note it in the checker docstring, or add `.size`.

---

## What's good (keep it)

- The round 1 fixes listed above. In particular:
  - the per-row optimistic mutation with `isMutating(...) === 1`
  - the pre-16.2 `router.refresh()` + `reset()` pattern
  - the Load more button in the infinite list example (accessible, simpler than an intersection observer)
- `results.md`'s caveats section, which names the small sample, the text matching, the mid-run harness fix and the length cost.
- The checker's new walk test in `run_tests.py`, which catches fixtures a folder walk would skip.
- The scope table and trap evals.

## Done when

- [ ] SKILL.md is split into core and situational rules, has a proportionality rule, and is at or below about 2,100 words (P1).
- [ ] Evals 1, 2, 17 and T1 are re-run. `results.md` shows pass counts and line counts, and the line counts are well below the 576–682 seen in run 1.
- [ ] A triggering eval is added and run. At least one TanStack Query or Next.js case is run. Grading is done by an agent that didn't write the changes (P2).
- [ ] P3 model gaps are fixed in SKILL.md and examples.md.
- [ ] P4 rules are reworded to "use the existing mechanism or report it missing".
- [ ] P5 example bugs are fixed.
- [ ] P6.1–6.3 have fixtures and fixes, the Next.js page fixtures throw `Error`, and `python3 dev/ui-states/tests/run_tests.py` passes.
- [ ] README's ui-states section still matches the skill.

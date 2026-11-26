# Eval results

## Summary

The skill reliably adds timeouts and clear empty states, triggers on the right prompts, and stays out of the trap. Round 2 cut its output from about 6 times the no-skill length to under 2 times. The remaining extra is mostly inline styles and a one-line offline message.

| Case | With skill (run 4) | Without skill | Graded by |
|---|---|---|---|
| **1. Empty list** | 3 of 3 | 3 of 3 (harness), 0 of 3 (grader) | both |
| **2. HTTP 500** | 3 of 3 | 3 of 3 | both |
| **17. Request never resolves** | 3 of 3 | 0 of 3 | both |
| **9. TanStack refetch fails with cached data** | 3 of 3 | 3 of 3 | both |
| **T1. Static nav (trap, run 2)** | 3 of 3 | 3 of 3 | both |
| **Triggering** | 8 of 8 | n/a | script |

| Lines | Run 1 | Run 2 | Run 3 | Run 4 | Without skill |
|---|---|---|---|---|---|
| **Users component** | 576, 658, 682 | 216, 251, 264 | 226, 237, 251 | 184, 188, 236 | 102, 111, 111 |
| **TanStack orders** | not run | 319, 323, 369 | 276, 287, 309 | 262, 262, 278 | 113, 144, 195 |
| **Nav (T1)** | 18, 20, 20 | 18, 18, 22 | not run | not run | 23, 32, 32 |

Run 4 is about 1.9 times the no-skill baseline for users and 1.8 times for orders, on average. That meets the round 2 target of under 2 times.

## What each run changed

| Run | Skill version | Change |
|---|---|---|
| **1** | Round 1 | First measurement. Strict case 1 (needed an action). |
| **2** | Round 2: core and situational split, proportionality rule, `reference.md` | Skill re-run for users, nav and orders. No-skill outputs from run 1 re-blinded and re-graded with the tightened harness. |
| **3** | Round 2 plus four fixes the run 2 grader pointed to | Offline only if the app supports it. Refresh branches only if the view refetches. No per-status errors in the core example. No new delay hooks. |
| **4** | Run 3 plus a conditional status rule | "Keep the status only if the UI branches on it." The core snippet and example dropped the error payload. `HttpError` moved to its own example. Skill condition only. |

## Findings

- **Timeouts:** the clearest win. With the skill, every users component gave up after 10 s and showed Retry. Without it, all 6 still said "Loading users…" after 30 s.
- **Case 1 without the skill:** the graders disagree. "No users yet." passes the harness, but the independent grader failed it because it doesn't say what will appear, as eval 1 asks. Both graders passed every skill output.
- **TanStack case 9:** a tie. All 12 outputs kept cached orders with a "Couldn't refresh" notice. The model already knows this pattern without the skill.
- **Status tables:** gone in run 4. In run 3, per-status error tables (401, 403, 5xx) were the main extra. They traced to the rule "throw an error that keeps the status, so the UI can pick the recovery". Making it conditional removed them.
- **The remaining extra length**, per the independent grader:
  - inline style objects of 80 to 90 lines
  - a one-line offline message in the TanStack outputs, which the grader did not count as unasked-for infrastructure
  - small extras, like a response-shape check

  The styles come mostly from the eval's own constraint: one self-contained file, with no project components to reuse.
- **Shorter description, tested and rejected:** I cut the `description` from 81 to 60 words. Triggering on "Show a list of users from `/api/users`" dropped to 2 of 4 runs. The current description loaded it 3 of 3. The saving was about 20 words per session, so the current description stays.
- **Triggering:** the skill loaded for all 4 prompts that should load it: list, search, form and review. It loaded for none of the 4 near misses: static nav, typo fix, prop rename and price formatter.

## Method

- **Model:** Claude Opus 5.5, one fresh agent per output, 3 outputs per condition.
- **With skill:** told to read `SKILL.md` (and optionally `examples.md` and `reference.md`) and follow it. **Without:** told to read no files.
- **Constraints, both conditions:** one React 19 + TypeScript file, imports only from `react` (plus `@tanstack/react-query` for orders), plain `fetch`.
- **Blinding:** outputs got random IDs, re-randomized each run. Both graders finished before unblinding.
- **Harness grader:** `harness/users.test.tsx` and `harness/orders.test.tsx` render each output in jsdom with a mocked `fetch`.
- **Independent grader:** a separate agent that read only `evals.md` and the blinded files. It never saw the skill, the harness or the mapping.
- **Triggering:** `harness/trigger.sh` runs `claude -p` in a scratch project with only `ui-states` installed, in plan mode, and checks whether the `Skill` tool loads `ui-states`.

## Caveats

- **Small sample:** 3 outputs per condition, one model. Only the case 17 gap and the line counts are strong signals.
- **Reused baseline:** runs 2 and 3 reused run 1's no-skill users outputs (and run 2's no-skill orders), since that condition didn't change.
- **Run 4:** the scratch folder holding runs 1 to 3 was cleared by the system, so run 4 generated only the skill condition. It was compared with the recorded no-skill line counts and graded blind, but with no no-skill files mixed in.
- **Harness text matching:** it finds states by visible text. It skips `<style>`, `[hidden]` and common screen-reader-only classes, but jsdom has no CSS, so other hidden text still counts.
- **Harness fixes:** run 1 fixed text gluing and inline CSS before unblinding. Run 2 dropped "nothing" from the empty match, banned "Nothing to see here", and fixed an output ID bug before unblinding.
- **Triggering:** one run per prompt, capped at 4 turns. A prompt could load the skill later in a longer session.
- **Not covered:** Next.js cases, and 20 of the 27 cases.

## Next

- **Decide case 1:** is "No users yet." enough, or must the text say what will appear? The two graders split on it.
- **Run more cases:** a Next.js case (11 or 26), and the forms cases (6, 16, 18).

## Rerun

```
cd dev/ui-states/harness && npm install
# put each output at outputs/<id>/Users.tsx or outputs/<id>/Orders.tsx, then:
npx vitest run        # writes results-users.json and results-orders.json
cd ../../.. && sh dev/ui-states/harness/trigger.sh
```

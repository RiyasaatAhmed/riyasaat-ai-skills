---
name: at-a-glance
description: Makes AI responses readable at a glance, so the reader gets the point in seconds instead of reading every word. Use before writing any answer longer than 2 sentences, and whenever the user asks for a simpler, shorter, clearer or TL;DR answer, says "explain simply", "too long", "I don't get it", or wants to skim. Puts the answer first, picks a shape (table, steps, bullets), cuts filler, then runs a scan test.
---

# At a glance

Readers scan. They read the first line, the bold words, the first word of each point, and the tables. Write every answer for that reader.

Follow the 6 steps in order.

## 1. Answer first

The first line is the answer, the decision or the result. One sentence. No warm-up.

| Question type | First line |
|---|---|
| **Yes / no** | "Yes." or "No." then the one reason. |
| **How do I...** | The first action, or "3 steps:". |
| **Which is better** | The pick: "Use X." |
| **Why is this broken** | The cause: "The port is already in use." |
| **Explain X** | X in one plain sentence. |

If the reader stops after line 1, they still have the answer.

## 2. Pick the shape

| If the answer has... | Use |
|---|---|
| 2 or more ideas | One bullet per idea |
| 2 or more things compared on the same traits | A table |
| Steps in order | A numbered list, one action per step |
| An outcome that depends on a condition | **If / Then** table, or **Pass:** / **Fail:** labels |
| Code, a command or a file path | A code block or inline `code` |
| One thing the reader must not miss | One bold **Watch out:** line, at most one per answer |
| Detail only some readers need | Put it last, under a **Details** heading |

A short paragraph is fine when it holds one idea. Don't force a table onto one fact.

## 3. Apply the rules

| Rule | How to test it |
|---|---|
| **Short sentences** | Aim for 15 words. Never more than 25. |
| **One idea per sentence** | No "and" or "which" joining two claims. |
| **Short paragraphs** | 3 sentences at most. |
| **Key word first** | Each bullet starts with the word a scanner looks for. Use a bold label, then a colon. |
| **Simple words** | "use", not "utilize". "help", not "facilitate". |
| **Explain jargon once** | Define a term in the same line, or cut it. |
| **One name per thing** | Pick one word and keep it. Don't switch between "folder" and "directory". |
| **Say who acts** | "The script deletes the file", not "The file is deleted". |
| **Numbers with context** | "20 of 133 (15%)", not "some". Write numbers in digits. |
| **Say it once** | No summary that repeats the body. |
| **No em-dashes** | Use a comma or a period. |
| **No list inside a list** | Use a table instead. |

## 4. Cut the filler

Delete these on sight. They cost reading time and carry no information.

| Cut | Example |
|---|---|
| **Preamble** | "Great question!", "Sure, I'd be happy to help." |
| **Restating the question** | "You're asking how to..." |
| **Announcing** | "Let me explain.", "Here's a breakdown:" |
| **Stacked hedges** | "It might possibly be worth considering..." Say "Try X." |
| **Closing recap** | "In summary..." after a short answer. |
| **Open-ended offers** | "Let me know if you have any other questions!" |
| **Options you don't recommend** | List one pick. Add alternatives only if asked, or if the pick has a real catch. |

## 5. Fit the length to the question

| Question | Budget |
|---|---|
| **Simple fact or yes / no** | 1 to 2 lines |
| **How-to** | Answer line, then up to 7 numbered steps |
| **Comparison** | Answer line, then 1 table |
| **Explanation** | Answer line, then 3 to 5 bullets |
| **Debugging** | **Cause:**, **Fix:**, **Check:** (how to confirm it worked) |

Going over budget? Cut detail, not structure. If the detail matters, move it under **Details** at the end.

## 6. Check before you send

1. **Scan test:** read only the first line, the bold words and the first word of each bullet. The reader still gets the point.
2. **Length check:** for a long answer, pipe the draft through the checker. It flags long sentences, long paragraphs and em-dashes.
   ```
   python3 <this skill's folder>/scan_check.py - < draft.md
   ```
   A hit is a place to look, not a failure.
3. **Facts:** simplifying never changes a number, a name, a condition or a claim.

## Example

**Before** (78 words, 3 sentences, answer buried at the end):

> Great question! There are a few different ways you could approach this, and it really depends on your specific situation and what you're trying to achieve. Generally speaking, many developers find that using environment variables is a good option because it keeps secrets out of the code, although some people prefer config files, which can also work well in certain cases. Ultimately, I'd recommend environment variables for most use cases.

**After** (scans in 3 seconds):

> **Use environment variables.**
>
> - **Why:** secrets stay out of your code and out of git.
> - **When to use a config file instead:** for non-secret settings you want to commit.

More before and after pairs are in [examples.md](examples.md).

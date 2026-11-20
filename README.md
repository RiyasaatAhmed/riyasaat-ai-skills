# Riyasaat's AI skills

Agent skills for Claude Code, Claude.ai, Codex, Cursor and other agents that read `SKILL.md`.

## Skills

| Skill | What it does |
|---|---|
| [at-a-glance](skills/at-a-glance) | Makes AI answers readable in seconds: answer first, tables and steps, no filler. |

## Install

**Any agent, with the skills CLI:**

```
npx skills add RiyasaatAhmed/riyasaat-ai-skills                   # all skills
npx skills add RiyasaatAhmed/riyasaat-ai-skills --skill at-a-glance  # one skill
```

**Claude Code, as a plugin:**

```
/plugin marketplace add RiyasaatAhmed/riyasaat-ai-skills
/plugin install at-a-glance@riyasaat-ai-skills
```

**Claude Code, by hand:** copy a folder from `skills/` to `~/.claude/skills/`.

**Claude.ai:** zip a folder from `skills/` and upload it under Settings, Capabilities, Skills.

## at-a-glance

| Step | What changes |
|---|---|
| **Answer first** | Line 1 is the answer. No warm-up. |
| **Shape** | A short paragraph by default. Tables for comparisons, numbered lists for steps. Bold only labels and one key phrase. |
| **Rules** | Short sentences, short paragraphs, plain words. Targets, not laws. |
| **Cut filler** | No "Great question!", no recaps, no stacked hedges. |
| **Length budget** | A yes / no question gets 1 to 2 lines. Asking for depth skips the budget. |
| **Scan test** | Read only the first line and first words. The point still lands. |
| **Facts stay** | Shorter never drops a warning or a condition, or sounds surer than the facts. |

**Make it always on:** Claude loads a skill when the request matches its description. To apply it to every answer, add this line to your `CLAUDE.md`:

```
Use the at-a-glance skill for every answer longer than 2 sentences.
```

**Check a draft:** `scan_check.py` flags long sentences, long paragraphs, em-dashes, filler phrases and bolded whole sentences. It needs only Python 3, and prints nothing when the text is clean.

```
python3 skills/at-a-glance/scan_check.py - < draft.md
```

See [examples.md](skills/at-a-glance/examples.md) for before and after pairs, and [evals.md](skills/at-a-glance/evals.md) for test cases to run after a change.

## Add a new skill

1. Copy `template/` to `skills/<skill-name>/`.
2. Set `name:` in `SKILL.md` to the folder name.
3. Add a row to the **Skills** table above.
4. Add a plugin entry to `.claude-plugin/marketplace.json`.

**Naming rules** (from the [Agent Skills spec](https://github.com/agentskills/agentskills/blob/main/docs/specification.mdx)):

| Rule | Example |
|---|---|
| **Lowercase letters, digits and single hyphens** | `at-a-glance`, not `At_A_Glance` |
| **64 characters at most** | |
| **Folder name matches `name:`** | `skills/at-a-glance/` holds `name: at-a-glance` |
| **No "claude" or "anthropic"** | These words are reserved. |
| **Say what it does** | Anthropic suggests a verb form like `writing-commits`. Short names like `tldr` are also common. |

## License

[MIT](LICENSE)

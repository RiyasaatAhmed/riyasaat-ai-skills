# Riyasaat's AI skills

Agent skills for Claude Code, Claude.ai, Codex, Cursor and other agents that read `SKILL.md`.

## Skills

### Writing

| Skill | What it does |
|---|---|
| [at-a-glance](skills/at-a-glance) | Makes AI answers readable in seconds: answer first, tables and steps, no filler. |

### Frontend

| Skill | What it does |
|---|---|
| [ui-states](skills/ui-states) | Makes AI-built UI handle loading, empty, error, partial, stale, offline and long-text states, not only the happy path. |

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
/plugin install ui-states@riyasaat-ai-skills
```

**Claude Code, by hand:** copy a folder from `skills/` to `~/.claude/skills/`.

**Claude.ai:** zip a folder from `skills/` and upload it under Settings, Capabilities, Skills.

## Updates

Every commit to `main` is a new version. No version number to bump.

| Installed with | Get updates |
|---|---|
| **Claude Code plugin** | Turn on auto-update once: `/plugin`, then **Marketplaces**, then `riyasaat-ai-skills`. Or update by hand with `/plugin marketplace update riyasaat-ai-skills`. |
| **Skills CLI** | `npx skills update` |
| **By hand or Claude.ai** | Copy or upload the folder again. |

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

## ui-states

| Part | What it does |
|---|---|
| **Proportion** | Only the states this data can reach. Reuses the project's components. Reports missing infrastructure instead of building it. |
| **Core** | Data tracked apart from the request, so a failed refresh keeps old data. Empty, loading, error with Retry, and a timeout. No `data = []` defaults, no leaked `0`, `res.ok` checked. |
| **Situational** | Search, lists, forms, optimistic updates, uploads, offline, permissions, images, translation and Next.js routes, each only when the feature has that trigger. The rules live in `reference.md`. |
| **Timing** | No spinner under ~300 ms. A first-load skeleton shows right away. 10 s or more gets a percent bar and Cancel. |
| **Announcements** | Mounted `role="status"` and `role="alert"` regions, and decorative loaders hidden from screen readers. |
| **Scope** | Static content gets no extra branches. Prop-only components get loading and error only if they are passed in. |
| **Review mode** | When reviewing, one line per surface: states handled, states missing, and `file:line`. |

See [examples/](skills/ui-states/examples) for before and after code, one file per topic, and [reference.md](skills/ui-states/reference.md) for the situational rules.

## Add a new skill

1. Copy `template/` to `skills/<skill-name>/`.
2. Set `name:` in `SKILL.md` to the folder name.
3. Add a row to the right group in the **Skills** table above, or a new group.
4. Add the skill to the same group in `skills.sh.json`.
5. Add a plugin entry to `.claude-plugin/marketplace.json`.

**Maintainer tools** go in `dev/<skill-name>/`, not in the skill folder. Installs copy only the skill folder, so users never get them.

| Tool | Run |
|---|---|
| **ui-states checker** | `python3 dev/ui-states/state_check.py path/to/src` flags leaked `0`s, swallowed errors, data with no error state, and more. Use it to grade eval outputs. |
| **Checker tests** | `python3 dev/ui-states/tests/run_tests.py`, after any change to the checker. CI runs it too. |
| **ui-states evals** | [dev/ui-states/evals.md](dev/ui-states/evals.md): test cases and traps to run after a change. Results are in `dev/ui-states/results.md`. |

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

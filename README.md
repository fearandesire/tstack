# tstack

This fork of [Theo Browne's tstack](https://github.com/t3dotgg/tstack) adds
explicit delegation instructions for Codex, Claude Code, and OpenCode alongside
the T3 Code route. Theo's skills and MIT attribution are retained.

The agent skills I use every day, cleaned up so anyone can use them. They work
in Claude Code and Codex. Some use [T3 Code](https://github.com/pingdotgg/t3code)
features when they are available and fall back to native tools when they are
not.

## Skills

| Skill | Say | What it does |
|---|---|---|
| `full-send` | "full send" | Takes a change to a merged PR with nobody watching: proves it, reviews it, files it, babysits it, merges it. |
| `full-stop` | "full stop" | Same as `full-send`, but stops when the PR is ready for you to merge. |
| `council` | "council" | Gets review from your chosen models, or three providers by default, and loops until they agree. |
| `sol-loop` | "sol loop" | Reviews a change with GPT Sol in a loop until both agents agree. |
| `file-pr` | "file a PR" | Files a short PR that leads with the problem, not an inventory of changes. |
| `takeover` | "take over" | Finishes someone else's PR, branch, or agent thread, and keeps their credit. |
| `babysit-pr` | "babysit" | Watches a PR through CI and review bots, and fixes the real findings. |
| `modernize` | "modernize" | Rebases an old PR and decides if it should still exist. |
| `leaving-pr-comments` | (automatic) | Formats comments that an agent posts on your behalf. |

Some skills call others. Install the ones they need too:

- `full-send` uses `sol-loop`, `file-pr`, and `babysit-pr`.
- `full-stop` uses `full-send`.
- `takeover` uses `modernize`, `file-pr`, `babysit-pr`, and `leaving-pr-comments`.
- `file-pr`, `babysit-pr`, and `modernize` use `leaving-pr-comments`.

## Install

```bash
git clone https://github.com/fearandesire/tstack
cp -R tstack/skills/* ~/.claude/skills/   # Claude Code
cp -R tstack/skills/* ~/.codex/skills/    # Codex
```

## Requirements

- An authenticated [GitHub CLI](https://cli.github.com) (`gh`).
- `python3` for `babysit-pr`'s `pr-wait` script.
- `council` and `sol-loop` need subagents on other providers' models. T3 Code
  does this with `delegate_task`. Otherwise you need a harness that can run
  those models.

## Make them yours

These are starting points. Edit them. Put personal settings, like which models
sit on your council, in your `CLAUDE.md` or `AGENTS.md`, so you can update the
skills without losing them.

## Choose reviewers

Name the models in your request, or save a council roster in your applicable
project or global instructions. Follow your harness's instruction hierarchy.
For example, replace the model placeholders with IDs your harness exposes:

```text
Run council with exactly <model-id-a> and <model-id-b>, at high effort.
```

That request selects two reviewers even if both use the same provider. Without
an explicit roster, council requests three models from different providers.
For saved defaults, state `Council members: ...` and `Sol-loop reviewer: ...`
in your instructions. The current request overrides those defaults. `sol-loop`
still requires a Sol model; council can use any explicitly chosen roster.

Each workflow explains model resolution, dispatch, result collection,
continuation, and cancellation for T3 Code, Codex, Claude Code, and OpenCode.
The instructions use the tools actually exposed in the current session.
OpenCode v2's `subagent` and older `task` tools have separate instructions.
Inside T3 Code, the T3 orchestration route takes precedence regardless of the
parent provider. Running `council` without a roster keeps Theo's three-provider,
high-effort default and the same score/report/fix-and-review workflow.

Native model access differs by harness. Codex's available model list may cover
one provider. Claude's native Agent model aliases select Claude models.
OpenCode selects models through configured agents unless its tool explicitly
supports an override. These skills use existing authorized routes. They report
missing models or runtime substitutions rather than creating a provider bridge
or silently selecting another model. Installing the skills does not add model
subscriptions or multi-provider access to Claude.ai.

## License

[MIT](LICENSE)

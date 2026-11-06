---
name: sol-loop
description: Use when the user says "sol loop".
---

# sol-loop

This is a workflow for making your code changes more correct before (or
sometimes after) filing a pull request. tl;dr - use OpenAI's GPT Sol to review
your code in a loop.

Make the most minimal possible changes to appease the Sol reviewers. Be careful
of scope creep and don't be scared to push back.

## Budget

- Default: 3 rounds total. Round 1 is full. Later rounds check only
  changed code and open findings.
- Extend to 5 only for security, permissions, auth, data loss, or
  state/concurrency, while a blocker or should stays open with evidence. Or when
  the user asks.
- Stop early if a round returns only nits. Declined nits and comment,
  doc, or format-only fixes need no new round.
- One reviewer only. Sol must not start subagents or reviewers.
- Keep a ledger: id, severity, outcome, usage if returned. Never guess it.

## 1. Scope

Run `git status --short`. Do not stash, discard, or include unrelated
changes. Limit review to the change paths if they separate cleanly.
Otherwise stop and ask.

Find the base after `git fetch origin`:

- PR: `gh pr view <n> --json baseRefName,headRefOid`. Check out the branch
  only if clean. Confirm `HEAD` is the PR head, or ahead only by this
  change. Base: `git merge-base HEAD origin/<baseRefName>`.
- Local: `git merge-base HEAD origin/<default-branch>`. No remote: a base
  the user names, or `HEAD` for uncommitted changes only.

The change is base to working tree in those paths, with untracked files.
Use one diff command all rounds. State intent and out-of-scope in 1-2
sentences. Run covering checks. Do not send code this change breaks. Note
missing or pre-failing checks in the brief.

## 2. Start Sol

Use the Sol version and effort in the current request, then applicable project
and global instructions, subject to the host's instruction hierarchy. Otherwise
resolve the latest available Sol through current capabilities. Keep the Sol
requirement: choosing a different reviewer is a different workflow. Inspect
exposed or discoverable tools and existing agent definitions first. Never call
an unlisted T3 tool to test whether it exists.
Resolve effort through a supported tool field or configured model variant.
If the route cannot express the requested effort, report that gap before dispatch.
When T3 orchestration is available, use its route even if the parent model runs
through Codex, Claude Code, or OpenCode. Use the native routes only outside T3;
a failed T3 request does not authorize switching routes.

- **T3 Code:** resolve the model with `orchestrator_capabilities`. Use
  `delegate_task` every round with the exposed review role and async mode.
  Save `taskId` and use a new `clientRequestId` per round. `childThreadId`
  is storage, not a continuation target. Use delegation, not thread-launch
  or thread-message tools. Select the provider instance and Sol model explicitly
  from capabilities. Use exposed `task_status` and `task_cancel` for ambiguous
  completion and cancellation respectively.
- **Codex:** use `spawn_agent` with an exact Sol ID from the live model list
  and the requested `reasoning_effort` if supported. Use `fork_turns: "none"`
  and a complete `message` when overrides require it. Save the returned agent
  ID/task name. Collect completion notices or use `wait_agent`. Continue a new
  round through `followup_task` on that target when exposed; `send_message`
  alone may not restart an idle agent. Use older `resume_agent`/`wait` tools
  only if this session exposes them. A Codex role name does not establish Sol.
- **Claude Code:** use `Agent` only with an existing custom subagent or connected
  route that is configured to run Sol. Native `model` aliases select Claude
  families; passing a GPT ID or naming an agent `sol` does not enable OpenAI.
  Set `Agent.effort` when supported, otherwise use an existing agent configured
  for the requested effort. A different model need not inherit parent effort.
  Save agent/task handles. Use background completion notices or the available
  task-output tool, then `SendMessage` to the saved ID, or `Agent.resume` when
  its schema advertises that field. If the route is one-shot, start the next
  round with the complete prior ledger. Do not create a bridge or change
  authentication for this review.
- **OpenCode:** select an existing configured subagent whose resolved provider,
  model, and variant match Sol. An agent without a model inherits the parent;
  do not assume an agent named `reviewer` uses Sol. In v2 use `subagent` with
  its advertised agent ID and prompt fields, save `sessionID`, and use its
  documented continuation field. In versions exposing `task`, use its actual
  `subagent_type` and task/session continuation fields. Do not invent per-call
  model overrides. Foreground returns the result; background requires its
  completion notice. A model catalog entry alone does not prove a working route.

Record requested identity, dispatch route, saved handle, and effective model and
effort when exposed. Label runtime identity unverified when unavailable. A
reported model or effort substitution does not satisfy the requested review.
If no available route selects Sol, report that capability gap before dispatch.
Keep existing provider
settings, credentials, and permissions intact.

Do not edit scoped files while review runs. Wait for the notice. Do not
poll or start a second reviewer. Timeout, error, or no reply is not
approval. On failure, cancel through the exposed interrupt/stop control and
verify that run stopped before restarting with the ledger. In Codex this is
`interrupt_agent` or the advertised older stop tool; in Claude use the exposed
task-stop control and returned task handle; in OpenCode use its session
interrupt/abort control. If stop cannot be confirmed, report that blocker rather
than start a duplicate. On an authentication failure, stop that route and report
the destination/status. Do not retry with another identity or credential.

Round 1 brief (T3 children get no history):

```
Review only. Do not edit, commit, push, comment on PRs, or start subagents.
Repo: <abs path> Base: <sha> Intent: <intent> Out of scope: <scope> Checks: <results>
See: git diff <base> [-- <paths>]; git status --short (read untracked).
Read surrounding code. Find bugs, broken callers, mismatch with intent.
Skip style unless it hides a bug. Hold to the smallest change. Flag code,
tests, or guards the intent does not need. Other paths, rare cases, small
perf, extra compat: nits.
blocker = intended case wrong. should = real bug callers will hit, in intent. nit = rest.
Reply:
VERDICT: APPROVE or CHANGES
S1 [blocker|should|nit] <file>:<line> <claim>. Fix: <suggestion> (stable ids)
```

## 3. Answer findings

Check each finding and severity yourself. Another path, rare case, or
small cost is a nit, whatever label it came with.

- Agree: smallest fix. Prefer delete or narrow over new lock, cache,
  helper, or option. Fix the case that happened. Add one focused test
  that fails without the fix, if intent needs it.
- Disagree: say why, with evidence (file:line, test, output).
- Out of scope or nit: decline in one line. List as follow-up.

Update the ledger. Re-run checks and `git diff --shortstat <base>`. If
review grew the diff, cut first. Do not agree just to end the loop.

## 4. Next round

Start one only if budget remains and a blocker or should is open, behavior code
changed, or approval does not cover the current behavior diff. Use a fresh
`delegate_task` in T3, or follow up the saved native ID. Send the round 1 brief,
the ledger (`fixed:` / `disagree:` / `declined:` + evidence), the same base
diff, and the change since last round. Tell Sol: open ids and changed code only.
Mark each old id `resolved` or `still open: <reason>`.

## 5. Stop and ship

Agreed: APPROVE on the current behavior diff, no blocker or should open,
no concern of your own. Stuck: an item stays disputed after two replies,
or budget ends. Show both sides in 2-3 lines each. The user decides.
Budget end is not approval.

Do not push during the loop. Push after agreement only if the user asked
to push, ship, or update the PR. If you push to a PR, add above the model
blurb:

`Reviewed with sol-loop: <N> rounds with <model>. Sol verdict: approved`.

Add `on <effort>` only if verified.

Report: rounds, model, what Sol changed, diff size before/after, fixed and
declined findings with reasons, usage if exposed (else say not), pushed or not.

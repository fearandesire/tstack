---
name: council
description: Trigger this if the user says 'council'.
---

# Council

Before an audit, address outstanding PR comments, fix known issues, and run
relevant checks. Give council the updated implementation; do not defer known
fixes until reviews return. If the user wants to discard the implementation
and explore new ideas, skip fixes to code being replaced.

Resolve the council before starting delegates. Use the roster in the current
request, then applicable project instructions, then global instructions,
subject to the host's instruction hierarchy. An explicit roster replaces the
whole default, including its size and provider mix. Honor two reviewers or
multiple models from one provider when requested. Otherwise use the latest
flagship model from each of three different providers at high reasoning effort.
Resolve current
model IDs from available capabilities; names such as Opus, Sol, and Gemini Pro
are examples, not pinned IDs.

For each seat record the requested provider, model, effort, and available
dispatch route. Resolve requested effort through that route's supported effort
field or configured model variant. If it cannot express effort explicitly
chosen by the user, report the gap before dispatch rather than approximate it.
For the default high effort, use a supported control when available, otherwise
request high effort in the brief and label the effective effort unverified.
Inspect the current tool
schemas and existing agent definitions
before choosing a route. A tool's model field does not imply arbitrary-provider
support. If any required seat is unavailable, report the missing route before
starting a partial council. The user can explicitly approve a reduced roster.
Keep existing authentication, provider settings, and permissions intact.

## Dispatch in the current harness

Use only tools exposed or discoverable in this session. Tool names can be
namespaced. Follow the live schema when a version differs from these examples.
When T3 orchestration is available, use the T3 Code route even if the parent
model runs through Codex, Claude Code, or OpenCode. The native routes below
apply outside T3. A T3 failure is not permission to switch to a native route.

### T3 Code

Use `orchestrator_capabilities` to resolve the roster and `delegate_task` to
start each seat in parallel with a complete brief. For reviews use the exposed
review role and asynchronous mode. Save each returned `taskId` and wait for its
completion notice. On another round use a fresh request ID and `delegate_task`;
a `childThreadId` is storage, not a continuation target. Do not create chats
or use thread-message tools as a replacement for delegation.
Preserve the default three-provider roster and high-effort request unless the
user's instructions choose another roster or effort. Set each target's provider
instance and model explicitly from capabilities so it does not inherit the
parent's model or select the target provider's first model accidentally.
Use `task_status` to resolve an ambiguous completion and `task_cancel` to stop
a failed or abandoned task when those controls are exposed.

### Codex

Use `spawn_agent` from the available collaboration tools. Select exact IDs from
its current model list and set `reasoning_effort` only where supported. When
model overrides require an isolated prompt, use `fork_turns: "none"` and put
the complete brief in `message`. Do not copy a model ID from another harness.
An `agent_type` selects a role, not proof of a particular model or provider.

Save each returned agent ID or task name. Start independent seats before waiting,
within the session's concurrency limit. Collect completion messages and use
`wait_agent` for pending work. For a new round, use `followup_task` with the
saved target when supported; `send_message` alone may not restart an idle agent.
Use `interrupt_agent` to stop a failed or abandoned run and confirm its state
before replacing it. Older Codex versions may expose `wait`, `resume_agent`,
and `close_agent`; use those only when their schemas are present.

Codex's native model list may contain only one provider. Different models in
that list do not satisfy the default three-provider council. Use another route
only if it is already configured, authorized, and exposes the required model.

### Claude Code

Use the exposed `Agent` tool with an advertised `subagent_type`. Per-call
`model` accepts the aliases its schema lists, rather than arbitrary provider
IDs. To request an exact model, select an existing custom agent whose model
definition resolves to that model. Do not override that definition with a
different family alias. A custom agent named `sol` does not establish Sol access.
Native Claude agents alone do not provide OpenAI or Google models.

Set `Agent.effort` when the live schema supports it. Otherwise select an
existing agent with the requested effort. Do not assume a reviewer using a
different model inherits the parent's effort.

Start independent reviewers together, using `run_in_background: true` when
supported. Save returned agent IDs and task handles. Collect completion notices
or use the exposed task-output tool. Continue a completed reviewer through
`SendMessage` to its saved ID on versions that support this, or `Agent`'s
`resume` field when advertised. Use the exposed stop tool, such as `TaskStop`,
with the returned task handle when cancellation is needed. A one-shot agent
without a resumable ID needs a new invocation with the complete prior ledger.

Check effective model and effort when task metadata exposes them. Claude model
allowlists and forced-model settings can override the requested model. Report
a model or effort mismatch rather than counting that run as the requested
review. If an external
provider requires a bridge, use only an existing authorized bridge with verified
model selection; creating one is a separate setup task.

### OpenCode

Inspect the available agents and their resolved model settings. A named agent
without its own model inherits the caller's model. Use an existing agent whose
provider/model and variant match the requested seat. A `provider/model#variant`
setting belongs to the agent or a documented override, not an invented tool field.

In OpenCode v2 use `subagent` with the configured agent ID, description, and
complete prompt according to its live schema. Save the returned `sessionID`.
Foreground calls return their result; background calls return a session handle
and later notify completion. Continue with that `sessionID` only through the
documented continuation field. In versions exposing `task`, select the configured
`subagent_type` and save its returned task/session ID; reuse it only through the
continuation field that version advertises. Do not translate a v2 session ID
into a guessed legacy argument. Use the exposed session interrupt/abort control
to cancel, and confirm that it stopped before replacement.

Use parallel independent calls only when supported, otherwise run the resolved
seats sequentially and report that. `opencode models` can identify available IDs,
but does not prove authentication or a successful review. If the available tool
cannot select the requested agent/model, report the missing capability.

## Collect the reviews

Record the dispatched route and model separately from the runtime's reported
effective model and effort. If runtime identity or effort is not exposed, say
which value is unverified. Do not invent it. A reported substitution fails
that seat. Capacity limits,
authentication errors, timeouts, and partial output are not completed reviews.
Report the affected seat and safe error, without changing models or credentials.

Give each delegate the request and relevant context. For review or feedback,
keep their work read-only. Collect their responses and summarize the useful
findings, disagreements, and recommended next steps.

For a code review, ask each delegate for a score out of 10.
Count each full review pass as one round.
A fresh review after fixes starts a new round.

If the work ends in a pull request, put the results in the PR description.
Put this section before the model and harness line at the end:

```markdown
## Council review

Rounds: 2

| Delegate | Round 1 | Round 2 |
| --- | --- | --- |
| Claude Opus | 7/10 | 9/10 |
| GPT Sol | 8/10 | 10/10 |
| Gemini Pro | 7/10 | 9/10 |
```

If a delegate gives no score, write `no score`. Do not invent one.
If the PR is open, edit the description. Do not post a comment for this.
If there is no PR, put the same results in the final reply only.

If you agree with their recommendations, make the changes and request a fresh
review after. Continue this process until all delegates are satisfied with the
outcome.

Do not let repeated reviews result in scope creep. It is your job to fight to
keep scope limited.

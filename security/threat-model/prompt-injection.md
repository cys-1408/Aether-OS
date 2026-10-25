# Prompt injection defense

## Scope

Documents, filenames, terminal output, web page snippets and notifications can
reach a model prompt. They are data, never instructions to the agent or to the
shell.

## Where defenses live

| Defense | Implementation |
| --- | --- |
| Data/instruction separation | prompts are assembled in `ai/runtime/inference/prompt_builder.py` + `miso/agent/context_builder.py` with fixed system-prompt sections the model may not alter |
| Injection heuristics | `miso/safety/prompt_injection_filter.py` flags imperative patterns ("ignore previous", "run the following") in retrieved content and strips them from planning context |
| Untrusted boundary | `miso/safety/untrusted_content_boundary.py` marks source for every context item; agent plans may only reference *capabilities*, never raw file instructions |
| No output execution | `miso/safety/no_shell_interpolation.py` — output can only shape schema-validated capability parameters |
| Plan review | consequential plans require user-visible preview (`miso/ui/plan_preview.py`) even when the model was not injected |
| Path scope | `miso/safety/path_scope.py` confines file actions to approved roots |
| Bounded loops | `miso/safety/bounded_loop_guard.py` escalates out of repetitive re-ask patterns (an injected file trying to loop the agent) |

## Residual risk

Heuristic injection filters are imperfect. The structural defenses (typed
schemas, broker permission checks, confirmation-before-side-effects, result
verification) are the load-bearing protection; the model filter is defense in
depth only.

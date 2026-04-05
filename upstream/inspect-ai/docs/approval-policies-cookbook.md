# Approval Policies Cookbook

## Overview

Inspect's `@approver` decorator lets you build fine-grained, programmatic
approval policies for tool-calling agents. This cookbook shows how to:

1. Validate tool arguments before execution
2. Reject dangerous command patterns outright
3. Scope checks to specific command segments (e.g. only the `docker run`
   sub-command, not `docker ps`)
4. Escalate ambiguous calls to a human or a downstream approver

The examples below are drawn from real agentic evaluation workflows where
the agent drives a Docker-based sandbox and must be prevented from mounting
sensitive host paths or running privileged containers.

---

## The `@approver` Decorator

An approver is an async function that receives:

| Parameter  | Type              | Description                                      |
|------------|-------------------|--------------------------------------------------|
| `message`  | `str`             | The raw user/assistant message that triggered the call |
| `call`     | `ToolCall`        | The tool call object (function name + arguments) |
| `view`     | `ToolCallView`    | Optional rendered view of the call               |
| `history`  | `list[ChatMessage]` | Full conversation history up to this point     |

It must return an `Approval` with one of four decisions:

| Decision    | Meaning                                                      |
|-------------|--------------------------------------------------------------|
| `approve`   | Allow the tool call to proceed                               |
| `reject`    | Block the call and return an error to the model              |
| `escalate`  | Pass the call to the next approver in the chain              |
| `terminate` | Abort the current sample entirely                            |

---

## Example: Docker Command Approval Policy

The following approver validates `docker run` calls made by an agent operating
inside a sandboxed evaluation environment. It enforces three rules:

1. **Volume mount enforcement** — only allow mounts under `/workspace`
2. **Privileged flag rejection** — never allow `--privileged` or `--cap-add`
3. **Escalation pattern detection** — escalate calls that look like
   privilege-escalation attempts (e.g. mounting `/etc` or `/proc`)

```python
import shlex
from inspect_ai.approval import Approval, Approver, approver
from inspect_ai.model import ChatMessage
from inspect_ai.tool import ToolCall, ToolCallView


# Paths that are always forbidden as mount sources
_FORBIDDEN_MOUNT_PREFIXES = ("/etc", "/proc", "/sys", "/dev", "/root")

# Flags that grant excessive privileges
_PRIVILEGE_FLAGS = {"--privileged", "--cap-add", "--security-opt"}


@approver
def docker_policy(
    allowed_mount_root: str = "/workspace",
    allow_network: bool = False,
) -> Approver:
    """
    Approve, reject, or escalate docker tool calls.

    Args:
        allowed_mount_root: Only volume mounts whose source starts with
            this path are permitted. Defaults to "/workspace".
        allow_network: Whether to allow --network flags other than
            "none". Defaults to False (network-isolated containers only).
    """

    async def approve(
        message: str,
        call: ToolCall,
        view: ToolCallView,
        history: list[ChatMessage],
    ) -> Approval:
        # Only intercept docker calls; pass everything else down the chain
        if call.function != "bash":
            return Approval(decision="escalate", explanation="Not a bash call")

        raw_cmd = str(next(iter(call.arguments.values()), "")).strip()

        # Only apply docker-specific rules to `docker run` sub-commands
        if not _is_docker_run(raw_cmd):
            return Approval(decision="escalate", explanation="Not a docker run command")

        try:
            tokens = shlex.split(raw_cmd)
        except ValueError as exc:
            return Approval(
                decision="reject",
                explanation=f"Could not parse command: {exc}",
            )

        # --- Rule 1: Reject privilege-escalation flags ---
        for token in tokens:
            flag = token.split("=")[0]  # handle --flag=value syntax
            if flag in _PRIVILEGE_FLAGS:
                return Approval(
                    decision="reject",
                    explanation=(
                        f"Privilege flag '{flag}' is not permitted. "
                        "Remove --privileged, --cap-add, and --security-opt."
                    ),
                )

        # --- Rule 2: Validate volume mounts ---
        for i, token in enumerate(tokens):
            if token in ("-v", "--volume") and i + 1 < len(tokens):
                mount_spec = tokens[i + 1]
                host_path = mount_spec.split(":")[0]
                if any(host_path.startswith(p) for p in _FORBIDDEN_MOUNT_PREFIXES):
                    return Approval(
                        decision="terminate",
                        explanation=(
                            f"Mount source '{host_path}' is a sensitive system path. "
                            "Terminating sample to prevent host escape."
                        ),
                    )
                if not host_path.startswith(allowed_mount_root):
                    return Approval(
                        decision="reject",
                        explanation=(
                            f"Mount source '{host_path}' is outside the allowed root "
                            f"'{allowed_mount_root}'. Only mounts under "
                            f"{allowed_mount_root} are permitted."
                        ),
                    )

            # Handle --volume=src:dst syntax
            if token.startswith("--volume=") or token.startswith("-v="):
                mount_spec = token.split("=", 1)[1]
                host_path = mount_spec.split(":")[0]
                if any(host_path.startswith(p) for p in _FORBIDDEN_MOUNT_PREFIXES):
                    return Approval(
                        decision="terminate",
                        explanation=(
                            f"Mount source '{host_path}' is a sensitive system path."
                        ),
                    )

        # --- Rule 3: Network isolation ---
        if not allow_network:
            has_network_flag = any(
                t.startswith("--network") and "none" not in t for t in tokens
            )
            if has_network_flag:
                return Approval(
                    decision="reject",
                    explanation=(
                        "Network access is disabled for this evaluation. "
                        "Use --network=none or omit the --network flag."
                    ),
                )

        return Approval(decision="approve", explanation="docker run command is safe")

    return approve


def _is_docker_run(cmd: str) -> bool:
    """Return True if the command is a `docker run` invocation."""
    parts = cmd.split()
    # Accept: docker run ..., docker  run ..., sudo docker run ...
    try:
        idx = parts.index("docker")
        return idx + 1 < len(parts) and parts[idx + 1] == "run"
    except ValueError:
        return False
```

---

## Wiring the Policy into an Evaluation

Approvers are composed into a **policy chain** — each approver handles the
calls it recognises and escalates the rest. The last approver in the chain
acts as the catch-all:

```python
from inspect_ai import eval
from inspect_ai.approval import ApprovalPolicy, auto_approver, human_approver

# Evaluation-level approval policy
approval = [
    # Docker-specific rules applied first
    ApprovalPolicy(
        docker_policy(allowed_mount_root="/workspace", allow_network=False),
        tools=["bash"],
    ),
    # Human review for any other tool calls that weren't approved above
    ApprovalPolicy(human_approver(), tools="*"),
]

eval("agent_eval.py", approval=approval, trace=True)
```

Or equivalently in YAML:

```yaml
approvers:
  - name: mypackage/docker_policy
    tools: "bash"
    allowed_mount_root: "/workspace"
    allow_network: false

  - name: human
    tools: "*"
```

---

## Scoping Checks to Command Segments

A common mistake is applying broad string-matching to the entire command.
Instead, parse the command with `shlex.split()` and inspect only the relevant
segment. For `docker run`, the relevant segment starts after the image name:

```python
def _docker_run_args(tokens: list[str]) -> list[str]:
    """Return only the docker run flags (before the image name)."""
    try:
        run_idx = tokens.index("run")
    except ValueError:
        return []
    # Flags appear between 'run' and the image name (first non-flag token)
    flags = []
    for token in tokens[run_idx + 1:]:
        if token.startswith("-"):
            flags.append(token)
        else:
            break  # image name reached
    return flags
```

This avoids false positives where the *container command* (not the docker
flags) happens to contain a string like `--privileged`.

---

## Escalation Pattern Detection

Some commands are not clearly safe or unsafe — they warrant human review.
Use `decision="escalate"` to pass them to the next approver in the chain:

```python
_ESCALATION_PATTERNS = [
    "nsenter",       # namespace entry — potential container escape
    "unshare",       # namespace manipulation
    "chroot",        # chroot jail escape
    "/proc/self",    # procfs self-reference
]

async def approve(...) -> Approval:
    for pattern in _ESCALATION_PATTERNS:
        if pattern in raw_cmd:
            return Approval(
                decision="escalate",
                explanation=(
                    f"Command contains escalation pattern '{pattern}'. "
                    "Routing to human review."
                ),
            )
    ...
```

---

## Testing Your Approver

Approvers are plain async functions — you can unit-test them directly without
running a full evaluation:

```python
import asyncio
from inspect_ai.tool import ToolCall

async def test_docker_policy():
    policy = docker_policy(allowed_mount_root="/workspace")

    # Should approve a safe mount
    safe_call = ToolCall(
        id="1", function="bash",
        arguments={"cmd": "docker run -v /workspace/data:/data ubuntu ls"},
        type="function",
    )
    result = await policy(message="", call=safe_call, view=None, history=[])
    assert result.decision == "approve"

    # Should reject a forbidden mount
    bad_call = ToolCall(
        id="2", function="bash",
        arguments={"cmd": "docker run -v /etc/passwd:/etc/passwd ubuntu cat /etc/passwd"},
        type="function",
    )
    result = await policy(message="", call=bad_call, view=None, history=[])
    assert result.decision == "terminate"

asyncio.run(test_docker_policy())
```

---

## See Also

- [Tool Approval](approval.qmd) — full reference for the approval system
- [Approver Extensions](extensions.qmd#sec-extensions-approvers) — packaging
  approvers for reuse across evaluations
- [Agents](agents.qmd) — building the agent solvers that approvers govern

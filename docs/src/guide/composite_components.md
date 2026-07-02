# Composite Components

Composite components are reusable, prebuilt subgraphs in MASFactory. They are implemented with standard `Graph`/`Loop`/`Agent` primitives, and can be created directly as nodes inside your `RootGraph`.

Common built-in composite components include:

- `VerticalGraph`
- `VerticalDecisionGraph`
- `VerticalSolverFirstDecisionGraph`
- `HorizontalGraph`
- `AdjacencyListGraph`
- `AdjacencyMatrixGraph`
- `BrainstormingGraph`
- `GeneratorVerifierGraph`
- `HubGraph`
- `MeshGraph`
- `InstructorAssistantGraph`
- `PingPongGraph`

Import them from `masfactory` directly and use them like any other graph node.

Most composite components take keyword-style configuration. In declarative graphs, use `NodeTemplate(...)`
to pass those kwargs.

---

## Minimal example: embed a HorizontalGraph

`HorizontalGraph` is a prebuilt sequential pipeline:
`ENTRY -> node[0] -> node[1] -> ... -> EXIT`.

### Declarative (recommended)

```python
from masfactory import CustomNode, HorizontalGraph, NodeTemplate, RootGraph

Pipeline = NodeTemplate(
    HorizontalGraph,
    node_args_list=[
        {"cls": CustomNode, "name": "a", "forward": lambda d: {"x": int(d["n"]) + 1}},
        {"cls": CustomNode, "name": "b", "forward": lambda d: {"y": int(d["x"]) * 2}},
    ],
    edge_keys_list=[{"x": "a output"}],
)

g = RootGraph(
    name="composite_demo",
    nodes=[("pipeline", Pipeline)],
    edges=[
        ("entry", "pipeline", {"n": "input number"}),
        ("pipeline", "exit", {"y": "final output"}),
    ],
)

g.build()
out, _attrs = g.invoke({"n": 3})
print(out)  # {'y': 8}
```

---

## GeneratorVerifierGraph

`GeneratorVerifierGraph` is a prebuilt retry loop for generator-verifier workflows:

```text
controller -> generator -> verifier -> decision
decision -- rejected --> controller
decision -- accepted --> terminate
```

Use it when one node creates a candidate result and another node decides whether the result is good enough. If the verifier rejects the result, the loop retries until the verifier accepts it or `max_iterations` is reached.

By default, acceptance is detected from a boolean field named `accepted`, `verified`, or `success` in the verifier output. You can also pass `accept_condition_function` for custom acceptance logic.

```python
from masfactory import CustomNode, GeneratorVerifierGraph, NodeTemplate, RootGraph


def generate(input_msg: dict) -> dict:
    attempt = int(input_msg.get("attempt", 0)) + 1
    return {
        "attempt": attempt,
        "candidate": f"draft-{attempt}",
    }


def verify(input_msg: dict) -> dict:
    attempt = int(input_msg["attempt"])
    return {
        **input_msg,
        "accepted": attempt >= 2,
        "feedback": "accepted" if attempt >= 2 else "try once more",
    }


RetryingDraft = NodeTemplate(
    GeneratorVerifierGraph,
    generator=NodeTemplate(CustomNode, forward=generate),
    verifier=NodeTemplate(CustomNode, forward=verify),
    max_iterations=3,
    generator_input_keys={"attempt": "previous attempt counter"},
    generator_output_keys={"attempt": "attempt counter", "candidate": "candidate result"},
    verifier_output_keys={
        "attempt": "attempt counter",
        "candidate": "candidate result",
        "accepted": "whether the result passed verification",
        "feedback": "verifier feedback",
    },
)

g = RootGraph(
    name="generator_verifier_demo",
    nodes=[("draft", RetryingDraft)],
    edges=[
        ("entry", "draft", {"attempt": "initial attempt counter"}),
        ("draft", "exit", {"candidate": "accepted candidate"}),
    ],
)

g.build()
out, _attrs = g.invoke({"attempt": 0})
print(out)  # contains the accepted candidate from the verifier output
```

The generator and verifier can be `Agent` templates as well as `CustomNode` templates. For agent-based workflows, make the verifier return an explicit boolean field such as `accepted` so the decision switch can route reliably.

### Imperative (alternative)

```python
from masfactory import CustomNode, HorizontalGraph, RootGraph

g = RootGraph(name="composite_demo")

pipeline = g.create_node(
    HorizontalGraph,
    name="pipeline",
    node_args_list=[
        {"cls": CustomNode, "name": "a", "forward": lambda d: {"x": int(d["n"]) + 1}},
        {"cls": CustomNode, "name": "b", "forward": lambda d: {"y": int(d["x"]) * 2}},
    ],
    edge_keys_list=[{"x": "a output"}],
)

g.edge_from_entry(pipeline, {"n": "input number"})
g.edge_to_exit(pipeline, {"y": "final output"})

g.build()
out, _attrs = g.invoke({"n": 3})
print(out)  # {'y': 8}
```

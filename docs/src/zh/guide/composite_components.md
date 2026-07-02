# 复合组件

复合组件是 MASFactory 内置的可复用预设子图，基于标准 `Graph` / `Loop` / `Agent` 组合实现，可直接在 `RootGraph` 中作为节点使用。

常见内置复合组件包括：

- `VerticalGraph`
- `VerticalDecisionGraph`
- `VerticalSolverFirstDecisionGraph`
- `HorizontalGraph`
- `AdjacencyMatrixGraph`
- `BrainstormingGraph`
- `GeneratorVerifierGraph`
- `HubGraph`
- `MeshGraph`
- `InstructorAssistantGraph`
- `PingPongGraph`

可直接从 `masfactory` 导入，并按普通图节点方式使用。


## 示例：嵌入 HorizontalGraph

`HorizontalGraph` 是一个内置的串行流水线：
`ENTRY -> node[0] -> node[1] -> ... -> EXIT`。

### 声明式

```python
from masfactory import CustomNode, HorizontalGraph, NodeTemplate, RootGraph

Pipeline = NodeTemplate(
    HorizontalGraph,
    node_args_list=[
        {"cls": CustomNode, "name": "a", "forward": lambda d: {"x": int(d["n"]) + 1}},
        {"cls": CustomNode, "name": "b", "forward": lambda d: {"y": int(d["x"]) * 2}},
    ],
    edge_keys_list=[{"x": "a 的输出"}],
)

g = RootGraph(
    name="composite_demo",
    nodes=[("pipeline", Pipeline)],
    edges=[
        ("entry", "pipeline", {"n": "输入数字"}),
        ("pipeline", "exit", {"y": "最终输出"}),
    ],
)

g.build()
out, _attrs = g.invoke({"n": 3})
print(out)  # {'y': 8}
```

---

## GeneratorVerifierGraph

`GeneratorVerifierGraph` 是一个内置的 generator-verifier 重试循环：

```text
controller -> generator -> verifier -> decision
decision -- rejected --> controller
decision -- accepted --> terminate
```

适合“一个节点生成候选结果，另一个节点验证是否达标”的场景。验证失败时会回到 controller 继续重试，直到 verifier 接受结果，或达到 `max_iterations` 上限。

默认情况下，组件会从 verifier 输出中的 `accepted`、`verified` 或 `success` 布尔字段判断是否通过。也可以传入 `accept_condition_function` 自定义判断逻辑。

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
    generator_input_keys={"attempt": "上一轮尝试次数"},
    generator_output_keys={"attempt": "当前尝试次数", "candidate": "候选结果"},
    verifier_output_keys={
        "attempt": "当前尝试次数",
        "candidate": "候选结果",
        "accepted": "是否通过验证",
        "feedback": "验证反馈",
    },
)

g = RootGraph(
    name="generator_verifier_demo",
    nodes=[("draft", RetryingDraft)],
    edges=[
        ("entry", "draft", {"attempt": "初始尝试次数"}),
        ("draft", "exit", {"candidate": "通过验证的候选结果"}),
    ],
)

g.build()
out, _attrs = g.invoke({"attempt": 0})
print(out)  # 包含 verifier 输出中通过验证的候选结果
```

generator 和 verifier 既可以是 `CustomNode` 模板，也可以是 `Agent` 模板。使用 Agent 时，建议让 verifier 明确输出 `accepted` 这类布尔字段，方便 decision switch 稳定路由。

### 命令式

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
    edge_keys_list=[{"x": "a 的输出"}],
)

g.edge_from_entry(pipeline, {"n": "输入数字"})
g.edge_to_exit(pipeline, {"y": "最终输出"})

g.build()
out, _attrs = g.invoke({"n": 3})
print(out)  # {'y': 8}
```

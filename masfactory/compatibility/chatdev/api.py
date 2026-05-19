from __future__ import annotations

from pathlib import Path
from typing import Any

from masfactory.compatibility.chatdev.graph import ChatDevRootGraph
from masfactory.compatibility.chatdev.materialize import blueprint_to_chatdev_graph
from masfactory.compatibility.chatdev.parse import chatdev_document_to_blueprint
from masfactory.compatibility.common.builder import blueprint_to_graph
from masfactory.compatibility.common.graph_design_export import blueprint_to_graph_design_document
from masfactory.compatibility.common.loaders import load_mapping_source
from masfactory.compatibility.common.llm_options import ChatDevCompileOptions
from masfactory.compatibility.paths import maybe_export_graph_design
from masfactory.components.graphs.graph import Graph


def load_graph_from_chatdev_yaml(
    source: str | Path | bytes,
    *,
    graph_name: str = "chatdev_import",
    options: ChatDevCompileOptions | None = None,
    use_placeholder: bool = False,
    graph_design_path: str | Path | bool | None = None,
) -> ChatDevRootGraph | Graph:
    """Load ChatDev 2.0 workflow YAML or 1.x chain config into a MASFactory graph."""
    doc, input_path = load_mapping_source(source, label="ChatDev document")
    bp = chatdev_document_to_blueprint(doc, base_path=input_path)
    fmt = (bp.metadata or {}).get("chatdev", {}).get("format", "workflow")
    maybe_export_graph_design(
        bp,
        graph_design_path,
        source=f"chatdev_{fmt}",
        input_path=input_path,
    )
    if use_placeholder:
        return blueprint_to_graph(bp, graph_name=graph_name, source=f"chatdev_{fmt}")
    return blueprint_to_chatdev_graph(bp, graph_name=graph_name, options=options)


def chatdev_document_to_graph_design(
    doc: dict[str, Any],
    *,
    base_path: Path | str | None = None,
    source: str | None = None,
) -> dict[str, Any]:
    """Return a Visualizer-previewable ``{graph_design: ...}`` document from ChatDev export."""
    bp = chatdev_document_to_blueprint(doc, base_path=base_path)
    fmt = (bp.metadata or {}).get("chatdev", {}).get("format", "workflow")
    return blueprint_to_graph_design_document(bp, source=source or f"chatdev_{fmt}")

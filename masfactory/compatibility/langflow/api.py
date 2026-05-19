from __future__ import annotations

from pathlib import Path

from masfactory.compatibility.common.graph_design_export import blueprint_to_graph_design_document
from masfactory.compatibility.common.loaders import load_mapping_source
from masfactory.compatibility.common.names import slugify_node_name
from masfactory.compatibility.langflow.graph import LangflowRootGraph
from masfactory.compatibility.langflow.materialize import blueprint_to_langflow_graph
from masfactory.compatibility.langflow.parse import langflow_document_to_blueprint
from masfactory.compatibility.paths import maybe_export_graph_design
from masfactory.compatibility.common.llm_options import LangflowCompileOptions


def langflow_document_to_graph(
    doc: dict,
    *,
    graph_name: str = "langflow_import",
    options: LangflowCompileOptions | None = None,
    graph_design_path: str | Path | bool | None = None,
    input_path: str | Path | None = None,
) -> LangflowRootGraph:
    bp = langflow_document_to_blueprint(doc)
    maybe_export_graph_design(bp, graph_design_path, source="langflow", input_path=input_path)
    return blueprint_to_langflow_graph(bp, graph_name=graph_name, options=options)


def langflow_document_to_graph_design(doc: dict, *, source: str = "langflow") -> dict:
    """Return a Visualizer-previewable ``{graph_design: ...}`` document from Langflow JSON."""
    bp = langflow_document_to_blueprint(doc)
    return blueprint_to_graph_design_document(bp, source=source)


def load_graph_from_langflow_json(
    source: str | Path | bytes,
    *,
    graph_name: str = "langflow_import",
    options: LangflowCompileOptions | None = None,
    graph_design_path: str | Path | bool | None = None,
) -> LangflowRootGraph:
    """Load a Langflow JSON export and return an executable MASFactory graph."""
    doc, input_path = load_mapping_source(source, label="Langflow JSON")
    name = graph_name
    if name == "langflow_import" and input_path is not None:
        name = f"lf_{input_path.stem}"
    name = slugify_node_name(name, fallback="langflow_import")
    return langflow_document_to_graph(
        doc,
        graph_name=name,
        options=options,
        graph_design_path=graph_design_path,
        input_path=input_path,
    )

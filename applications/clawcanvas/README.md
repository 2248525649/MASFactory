# ClawCanvas

ClawCanvas is a MASFactory-based skill studio for designing, testing, and packaging workflows as reusable skills.

The first MVP in this directory focuses on four capabilities:

- build a workflow on a web canvas
- validate the workflow structure before execution
- execute supported nodes through MASFactory with a user-supplied API key
- export the workflow plus skill metadata as a publishable skill package

## Layout

```text
applications/clawcanvas/
├── backend/
│   ├── clawcanvas_backend/
│   │   ├── app.py
│   │   ├── compiler.py
│   │   ├── schema.py
│   │   ├── skill_packager.py
│   │   └── __init__.py
│   ├── requirements.txt
│   └── tests/
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── src/
```

## MVP Scope

Currently supported runtime node types:

- `start`
- `agent`
- `custom`
- `loop`
- `end`

Current runtime constraints:

- graph must be a DAG
- exactly one `start` and one `end`
- supported tool execution is runtime-bound for `builtin` tools and configured `api` tools; `mcp` entries still need an external connector layer
- knowledge and behavior rules are compiled into agent prompt context, not yet into dedicated retrievers or MCP-backed tools
- `custom` nodes currently support built-in transform modes: `passthrough`, `template`, `set`, `pick`
- `loop` nodes are compiled into subgraph-based MASFactory `Loop` nodes with explicit controller inputs and controller outputs

## Backend

The backend is a Flask application that exposes:

- `GET /api/health`
- `GET /api/demo`
- `POST /api/validate`
- `POST /api/run`
- `POST /api/export-skill`
- `POST /api/export-json`
- `GET /api/download-export`
- `POST /api/validate-skill`
- `POST /api/ai-authoring/field`

Install app-specific dependencies:

```bash
cd /local/lys/MASFactory
pip install -e .

cd applications/clawcanvas/backend
pip install -r requirements.txt
```

Run the backend:

```bash
python -m clawcanvas_backend.app
```

By default the backend serves the built frontend and API on `0.0.0.0:15051`.
Override with `CLAWCANVAS_HOST` and `CLAWCANVAS_PORT` if needed.

## Frontend

The frontend is a Vue + Vite application with a draggable node canvas.

Environment requirement: Node.js `>= 18` is strongly recommended. The current Vite toolchain will not run reliably on Node 12.

Install dependencies:

```bash
cd applications/clawcanvas/frontend
npm install
```

Run locally:

```bash
npm run dev
```

In production the built frontend calls the API through same-origin `/api`.

## Deploy On Port 15051

From the repository root:

```bash
applications/clawcanvas/deploy_15051.sh
```

The script installs backend dependencies, builds the frontend, and starts gunicorn on `0.0.0.0:15051`.
Open `http://127.0.0.1:15051/` locally, or expose port `15051` from the host.

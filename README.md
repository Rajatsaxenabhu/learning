# learning
uv init --bare
uv add "mcp[cli]"

# start server
uv run python main.py

curl -sf http://localhost:8010/health && echo READY



gisproject/
├── pyproject.toml            # move into backend/ once the frontend exists (see note below)
├── docker-compose.yml        # vllm + backend + frontend (+ postgis later)
├── .env.example
├── .gitignore                # __pycache__, .venv, node_modules, .env
├── README.md
│
├── backend/
│   ├── pyproject.toml
│   ├── app/                          # FastAPI layer (new)
│   │   ├── main.py                   # create_app(), lifespan: start MCP client + agent
│   │   ├── config.py                 # pydantic-settings (LLM URL, MCP command, CORS)
│   │   ├── deps.py                   # Depends(): agent, mcp manager, db session
│   │   ├── api/
│   │   │   ├── router.py             # includes all v1 routers
│   │   │   └── v1/
│   │   │       ├── chat.py           # POST /chat (SSE stream of agent events)
│   │   │       ├── sessions.py       # list/create/delete conversations (thread_id)
│   │   │       ├── tools.py          # GET /tools (what the MCP server exposes)
│   │   │       ├── layers.py         # upload/list/download GeoJSON layers
│   │   │       └── health.py
│   │   └── schemas/                  # request/response pydantic models
│   │       ├── chat.py               # ChatRequest, StreamEvent (token, tool_call, tool_result, map_update)
│   │       └── layers.py
│   │
│   ├── agent/                        # you have this
│   │   ├── graph.py                  # LangGraph definition
│   │   ├── state.py
│   │   ├── prompts.py                # system prompts (split out of code)
│   │   ├── llm/{config,model}.py
│   │   └── service/tools.py          # MCP tools -> LangChain tools
│   │
│   ├── client/                       # MCP client (you have this)
│   │   ├── manager.py, config.py, error.py
│   │   └── connect/{base,stdio,http}.py
│   │
│   ├── server/gismcp/                # MCP server (you have this)
│   │   ├── server.py, stdiomain.py
│   │   ├── config/logging.py
│   │   ├── tools/{vector,raster}/    # thin MCP tool wrappers
│   │   ├── operations/{vector,raster}/  # pure GIS logic (shapely/pyproj)
│   │   ├── schemas/{vector,raster}/
│   │   └── resources/
│   │
│   ├── storage/                      # layers/uploads on disk (gitignored)
│   ├── tests/{agent,client,server,api}/
│   └── Dockerfile
│
└── frontend/                         # React + Vite + TypeScript
    ├── package.json, vite.config.ts, tsconfig.json, index.html
    ├── Dockerfile
    └── src/
        ├── main.tsx, App.tsx
        ├── api/                      # client.ts, chat.ts (SSE reader), layers.ts
        ├── components/
        │   ├── map/                  # MapView.tsx (MapLibre GL), LayerPanel.tsx
        │   ├── chat/                 # ChatPanel.tsx, MessageList.tsx, ToolCallCard.tsx
        │   └── layout/
        ├── hooks/                    # useChatStream.ts, useLayers.ts
        ├── store/                    # zustand: layers, messages, session
        ├── types/                    # geojson + stream event types
        └── lib/




GIS MCP Server
│
├── Vector
│   │
│   ├── Geometry
│   │   ├── calculate_area
│   │   ├── calculate_length
│   │   ├── calculate_centroid
│   │   ├── buffer_geometry
│   │   ├── intersection
│   │   ├── difference
│   │   ├── union_geometries
│   │   ├── simplify_geometry
│   │   ├── convex_hull
│   │   ├── bounds
│   │   └── validate_geometry
│   │
│   ├── Projection
│   │   ├── transform_geometry
│   │   ├── get_crs_info
│   │   ├── is_projected_crs
│   │   └── calculate_utm_zone
│   │
│   └── Vector Data
│       ├── get_vector_metadata
│       ├── list_vector_layers
│       ├── get_vector_schema
│       ├── get_feature_count
│       ├── filter_features
│       ├── spatial_query
│       └── features_within_distance
│
└── Raster
    │
    ├── Metadata
    │   ├── get_raster_metadata
    │   ├── get_raster_crs
    │   ├── get_raster_bounds
    │   ├── get_raster_resolution
    │   └── get_raster_band_info
    │
    ├── Statistics
    │   ├── calculate_raster_statistics
    │   ├── calculate_percentiles
    │   ├── get_unique_values
    │   ├── calculate_histogram
    │   ├── get_pixel_value
    │   └── calculate_nodata_percentage
    │
    └── Processing
        ├── clip_raster
        ├── mask_raster
        ├── reproject_raster
        ├── resample_raster
        ├── merge_rasters
        ├── crop_raster
        ├── rasterize_vector
        └── polygonize_raster
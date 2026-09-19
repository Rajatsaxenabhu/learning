# learning
uv init --bare
uv add "mcp[cli]"

# start server
uv run python main.py

curl -sf http://localhost:8010/health && echo READY



import os
from dataclasses import dataclass


@dataclass
class ModelConfig:
    model: str = os.getenv("LLM_MODEL", "parable-qwen3-8b")
    base_url: str = os.getenv("LLM_URL", "http://localhost:8100").rstrip("/") + "/v1"
    api_key: str = "dummy"

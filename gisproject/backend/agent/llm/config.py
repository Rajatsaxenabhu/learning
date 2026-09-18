from dataclasses import dataclass


@dataclass
class ModelConfig:
    model: str = "qwen3-8b"
    base_url: str = "http://localhost:8100/v1"
    api_key: str = "dummy"
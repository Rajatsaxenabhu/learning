from langchain_openai import ChatOpenAI

from agent.config.llm import ModelConfig


model = ChatOpenAI(
    model=ModelConfig.model,
    base_url=ModelConfig.base_url,
    api_key=ModelConfig.api_key,
    stream_usage=True,
)
from langchain_openai import ChatOpenAI

from agent.llm.config import ModelConfig


model = ChatOpenAI(
    model=ModelConfig.model,
    base_url=ModelConfig.base_url,
    api_key=ModelConfig.api_key,
)
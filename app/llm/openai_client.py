from openai import OpenAI
from app.llm.base import BaseLLM
from app.core.config import Config

class OpenAILLM(BaseLLM):
    def __init__(self):
        self.api_key = Config.OPENAI_API_KEY
        self.model = Config.LLM_MODEL
        self.is_configured = bool(self.api_key)
        self.client = OpenAI(api_key=self.api_key, timeout=Config.LLM_HEALTH_TIMEOUT_SECONDS) if self.is_configured else None

    def probe(self):
        if not self.is_configured:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        self.client.models.list()

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        if not self.is_configured:
            raise RuntimeError("OPENAI_API_KEY is not configured")

        response = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0
        )
        return response.output_text.strip()
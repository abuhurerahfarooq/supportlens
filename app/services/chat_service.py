import time
from app.llm.openai_client import OpenAILLM

SUPPORT_SYSTEM_PROMPT = """
You are a professional customer support agent for a SaaS billing platform.
Be concise and accurate.
"""

class ChatService:

    def __init__(self):
        self.llm = OpenAILLM()

    def generate_reply(self, user_message: str):
        start = time.time()

        response = self.llm.chat(
            SUPPORT_SYSTEM_PROMPT,
            user_message
        )

        response_time = int((time.time() - start) * 1000)
        return response, response_time
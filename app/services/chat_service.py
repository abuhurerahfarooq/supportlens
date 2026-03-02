import logging
import time
from app.core.logging import log_event
from app.llm.openai_client import OpenAILLM

SUPPORT_SYSTEM_PROMPT = """
You are a professional customer support agent for a SaaS billing platform.
Be concise and accurate.
"""

FALLBACK_REPLY = (
    "I'm unable to reach the AI provider right now. "
    "I have recorded your message and a support agent can follow up shortly."
)

class ChatService:
    def __init__(self):
        self.llm = OpenAILLM()
        self.logger = logging.getLogger("supportlens.chat")

    def generate_reply(self, user_message: str):
        start = time.time()

        try:
            response = self.llm.chat(SUPPORT_SYSTEM_PROMPT, user_message)
        except Exception as exc:
            log_event(
                self.logger,
                logging.WARNING,
                "llm_chat_failed",
                error=str(exc),
                fallback_used=True,
                message_preview=user_message[:120],
            )
            response = FALLBACK_REPLY

        response_time = int((time.time() - start) * 1000)
        return response, response_time
"""
rag/llm_client.py

LLMClient class for communicating with the Qwen language model
through the local Ollama API.
"""

import requests

from app.config import settings


class LLMClient:
    def __init__(self, host: str = None, model: str = None):
        self.host = host or settings.ollama_host
        self.model = model or settings.ollama_model

    def generate(self, prompt: str, timeout=1800) -> str:
        """
        Generate a response from the language model.

        The default timeout of 1800 seconds (30 minutes) is effectively
        unlimited for this application, as normal responses typically take
        several seconds to a few minutes. However, it still provides a final
        limit to prevent a backend worker from remaining blocked indefinitely
        if Ollama becomes unresponsive or crashes.

        To disable the timeout completely, set the timeout to None:
            llm_client.generate(prompt, timeout=None)
        """
        url = f"{self.host}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=timeout,
            )
            response.raise_for_status()

        except requests.exceptions.ConnectionError as e:
            raise RuntimeError(
                "Could not connect to Ollama. "
                "Make sure the 'ollama serve' command is running."
            ) from e

        except requests.exceptions.Timeout as e:
            raise RuntimeError(
                f"Model response exceeded {timeout} seconds (timeout)."
            ) from e

        data = response.json()

        return data.get("response", "").strip()
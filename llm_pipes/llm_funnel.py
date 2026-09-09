import json
import os
from typing import Any
from dotenv import load_dotenv
import requests

load_dotenv()

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-5.6-luna-pro"
SYSTEM_PROMPT = "You are a helpful assistant."
QUERY_SUFFIX = ""

ALLOWED_TOOLS = ["openrouter:web_search"]
ALLOWED_LLM_MODELS = ["openai/gpt-5.6-luna-pro"]

# OpenRouterTool: {"type": "openrouter:web_search"}


def build_content(
    query: str,
    append_query_suffix: bool = False,
    image_url: str | None = None,
    video_url: str | None = None,
    audio_url: str | None = None,
    file_url: str | None = None,
) -> str | list[dict[str, Any]]:
    text = f"{query}{QUERY_SUFFIX}" if append_query_suffix else query

    parts: list[dict[str, Any]] = [{"type": "text", "text": text}]

    if image_url:
        parts.append({"type": "image_url", "image_url": {"url": image_url}})
    if video_url:
        parts.append({"type": "video_url", "video_url": {"url": video_url}})
    if audio_url:
        parts.append({"type": "input_audio", "input_audio": {"url": audio_url}})
    if file_url:
        parts.append({"type": "file", "file": {"url": file_url}})

    # Plain string when there are no media attachments
    if len(parts) == 1:
        return text
    return parts


def openrouter_request(
    query: str,
    model: str | None = None,
    use_web_search: bool = True,
    max_tokens: int | None = None,
    reasoning: bool = True,
    append_query_suffix: bool = True,
    system_prompt: str = SYSTEM_PROMPT,
    image_url: str | None = None,
    video_url: str | None = None,
    audio_url: str | None = None,
    file_url: str | None = None,
) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not model:
        model = DEFAULT_MODEL
    if not max_tokens:
        max_tokens = 4000
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is not set")

    tools: list[dict[str, str]] = []
    if use_web_search:
        tools.append({"type": "openrouter:web_search"})

    response = requests.post(
        OPENROUTER_API_URL,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        json={
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": build_content(
                        query=query,
                        append_query_suffix=append_query_suffix,
                        image_url=image_url,
                        video_url=video_url,
                        audio_url=audio_url,
                        file_url=file_url,
                    ),
                },
            ],
            "tools": tools,
            "tool_choice": "auto",
            "system": system_prompt,
            "max_tokens": max_tokens,
            "reasoning": {"enabled": reasoning},
        },
    )

    if not response.ok:
        raise RuntimeError(
            f"OpenRouter request failed ({response.status_code}): {response.text}"
        )

    data = response.json()
    print("OpenRouter API response:", json.dumps(data, indent=2))
    return data.get("choices", [{}])[0].get("message", {}).get("content") or ""

if __name__ == "__main__":
    query = "What is the capital of France?"
    response = openrouter_request(query)
    print(response)
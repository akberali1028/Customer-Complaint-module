from __future__ import annotations

import json
import os
from typing import TypeVar

from dotenv import load_dotenv
from groq import AsyncGroq
from pydantic import BaseModel

load_dotenv()

DEFAULT_MODEL = "openai/gpt-oss-20b"
FALLBACK_MODEL = "openai/gpt-oss-120b"
ModelT = TypeVar("ModelT", bound=BaseModel)


def _client() -> AsyncGroq:
    api_key = os.getenv("GROQ_API_KEY") or os.getenv("Project_key")
    if not api_key:
        raise RuntimeError("Missing GROQ_API_KEY in the repository-root .env file.")
    return AsyncGroq(api_key=api_key)


async def structured_completion(
    *, system_prompt: str, user_prompt: str, schema: type[ModelT], model: str = DEFAULT_MODEL
) -> ModelT:
    """Request schema-constrained JSON and validate it before graph state is updated."""
    completion = await _client().chat.completions.create(
        model=model,
        temperature=0,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": schema.__name__,
                "strict": True,
                "schema": schema.model_json_schema(),
            },
        },
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    content = completion.choices[0].message.content
    if not content:
        raise ValueError("The model returned no structured content.")
    return schema.model_validate(json.loads(content))

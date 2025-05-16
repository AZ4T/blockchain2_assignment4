# src/ai_client.py
import asyncio
from functools import lru_cache

from transformers import pipeline
from starlette.concurrency import run_in_threadpool

@lru_cache()
def _get_generator():
    """
    Lazily load (and cache) a local GPT-2 text‐generation pipeline.
    """
    return pipeline("text-generation", model="gpt2")

async def answer_query(prompt: str, max_new_tokens: int = 50) -> str:
    """
    Asynchronously run GPT-2 locally to complete the given prompt.
    """
    generator = _get_generator()
    # Offload the blocking .__call__ to a threadpool
    outputs = await run_in_threadpool(
        generator,
        prompt,
        max_new_tokens=max_new_tokens,
        do_sample=True,         # enable sampling
        temperature=0.7,        # control diversity
        top_p=0.9,              # nucleus sampling
        pad_token_id=generator.tokenizer.eos_token_id
    )
    return outputs[0]["generated_text"]

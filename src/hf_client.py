# src/hf_client.py
import os, httpx
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
HF_TOKEN = os.getenv("HF_API_TOKEN")
if not HF_TOKEN:
    raise RuntimeError("HF_API_TOKEN not set")

MODEL   = "distilgpt2"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL}"

async def generate_text_httpx(prompt: str, max_new_tokens: int = 100) -> str:
    headers = {
      "Authorization": f"Bearer {HF_TOKEN}",
      "Content-Type":  "application/json",
    }
    payload = {
      "inputs":     prompt,
      "parameters": {"max_new_tokens": max_new_tokens}
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(API_URL, headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
        return data[0].get("generated_text", "").strip()

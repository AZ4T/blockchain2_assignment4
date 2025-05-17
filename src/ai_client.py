# src/ai_client.py
from functools import lru_cache
from llama_cpp import Llama
from starlette.concurrency import run_in_threadpool

@lru_cache()
def _get_llm():
    # no leading slash → project-relative path
    return Llama(model_path="models/llama-2-7b-chat.Q4_0.gguf",
                n_ctx=1024,
                use_mlock=True)      # optional: keep weights in RAM

async def answer_query(prompt: str, max_tokens: int = 256) -> str:
    llm = _get_llm()

    def _sync_call():
        # wrap prompt in the Meta “chat” instruction tokens:
        chat_prompt = f"<s>[INST] {prompt} [/INST]</s>"
        raw = llm(
            prompt=chat_prompt,
            max_tokens=max_tokens,
            stop=["</s>"]
        )
        # llama-cpp returns a plain string
        text = raw["choices"][0]["text"]
        return text.lstrip()

    return await run_in_threadpool(_sync_call)

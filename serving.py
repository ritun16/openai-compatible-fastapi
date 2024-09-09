from fastapi import FastAPI, HTTPException, Request
import nest_asyncio
from pyngrok import ngrok, conf
import uvicorn
import hashlib
import time
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer
import sqlite3
import configs as cfg

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = "mock-gpt-model"
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.1
    top_p: Optional[float] = 0.9

class vLLMMetaLlama3_1():

  def __init__(self):
    # Replace with other LLMs of your choice
    model_id = "hugging-quants/Meta-Llama-3.1-8B-Instruct-GPTQ-INT4"
    self.llm = LLM(model=model_id) # Setup serving LLM
    self.tokenizer = AutoTokenizer.from_pretrained(model_id) # Set up tokenizer
  
  def __call__(self, temperature, top_p, max_tokens, messages):
    sampling_params = SamplingParams(temperature=temperature, top_p=top_p, max_tokens=max_tokens) # Pass LLM params
    prompts = self.tokenizer.apply_chat_template(messages, tokenize=False) # Templatize OpenAI compatiable chat messages
    outputs = self.llm.generate(prompts, sampling_params) # Generation stage
    generated_text = outputs[0].outputs[0].text
    return generated_text


def rate_limit():
    def decorator(func: Callable[[Request], Any]) -> Callable[[Request], Any]:
        usage: dict[str, list[float]] = {}

        @wraps(func)
        async def wrapper(request: Request, authorization: str) -> Any:
            # get the API key
            api_key = authorization[len("Bearer "):]
            if not api_key:
                raise HTTPException(status_code=400, detail="API key missing")
                
            conn = sqlite3.connect(cfg.DB_NAME, check_same_thread=False)
            c = conn.cursor()
            c.execute("SELECT email FROM api_keys WHERE api_key = ?", (api_key,))
            result = cursor.fetchall()
            if result:
                user_email = result[0][0]
            else:
                raise HTTPException(status_code=400, detail="Invalid API Key")
            # Close the connection
            conn.close()

            # create a unique identifier for the client
            unique_id: str = hashlib.sha256(user_email.encode()).hexdigest()

            # update the timestamps
            now = time.time()
            if unique_id not in usage:
                usage[unique_id] = []
            timestamps = usage[unique_id]
            timestamps[:] = [t for t in timestamps if now - t < cfg.time_period]

            if len(timestamps) < cfg.num_request:
                timestamps.append(now)
                return await func(request)

            # calculate the time to wait before the next request
            wait = cfg.time_period - (now - timestamps[0])
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Retry after {wait:.2f} seconds",
            )

        return wrapper

    return decorator


app = FastAPI(title="OpenAI-compatible API")

llm_server = vLLMMetaLlama3_1()

@app.post("/chat/completions")
@rate_limit()
async def chat_completions(request: ChatCompletionRequest, authorization: str = Header(...)):
    response_content = llm_server(temperature=request.temperature, top_p=request.top_p, max_tokens=request.max_tokens, messages=request.messages)

    return {
        "id": hashlib.sha256(str(request.messages).encode()).hexdigest(),
        "object": "chat.completion",
        "created": time.time(),
        "model": request.model,
        "choices": [{
            "message": ChatMessage(role="assistant", content=response_content)
        }]
    }

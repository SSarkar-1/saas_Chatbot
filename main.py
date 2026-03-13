import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))
from fastapi import FastAPI
from pydantic import BaseModel
from app.retrieval.retriever import load_retriever
from app.llm.generator import generate_final_answer_stream
from app.utils.cache import get_cached_answer, store_cached_answer
from app.utils.history import append_history, get_history
import uvicorn
from fastapi.responses import StreamingResponse
import asyncio
from fastapi.middleware.cors import CORSMiddleware


app=FastAPI(title="AI Chatbot")


class AskRequest(BaseModel):
    query: str
    user_id: str = "default"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# query = "What is the formula for Scaled Dot-Product Attention?"
retriever=load_retriever()



async def stream_answer(payload: AskRequest):
    query = payload.query.strip().lower()
    user_id = (payload.user_id or "default").strip()

    cached = get_cached_answer(query=query)
    if cached:
        append_history(user_id, query, cached)
        yield cached
        return

    chunks = retriever.invoke(query)
    answer_accum = ""

    async for token in generate_final_answer_stream(query=query, chunks=chunks):
        answer_accum += token
        yield token
        await asyncio.sleep(0)  # allow other tasks

    if answer_accum:
        store_cached_answer(query, answer_accum)
        append_history(user_id, query, answer_accum)


@app.post("/ask")
async def ask(payload: AskRequest):
    return StreamingResponse(stream_answer(payload), media_type="text/plain")


@app.get("/history")
async def history(user_id: str = "default"):
    return {"history": get_history(user_id or "default")}

if __name__ == "__main__":
    # For production, use environment variable PORT (set by hosting platforms)
    port = int(os.environ.get("PORT", 8000))
    # Only enable reload in development
    reload = os.environ.get("ENVIRONMENT", "development") == "development"
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=reload)

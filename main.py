import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))
import asyncio
import re
from typing import Optional

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.retrieval.retriever import load_retriever
from app.llm.generator import generate_final_answer_stream
from app.utils.cache import get_cached_answer, store_cached_answer
from app.utils.db import record_message, fetch_history
from app.llm.query_rewrite import query_rewrite

load_dotenv()


app=FastAPI(title="AI Chatbot")


class AskRequest(BaseModel):
    query: str
    user_id: str = "default"
    session_id: Optional[str] = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# query = "What is the formula for Scaled Dot-Product Attention?"
retriever=load_retriever()


def preprocess_query(text):
    #remove case difference and trailing spaces
    text=text.lower().strip()
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text

async def stream_answer(payload: AskRequest):
    user_id = (payload.user_id or "default").strip()
    session_id = (payload.session_id or user_id or "default").strip()

    # Load recent conversation context (latest pairs)
    try:
        conversation_history = await fetch_history(session_id, keep=4)
        
    except Exception as e:
        print(f"[history] failed to load for context: {e}")
        conversation_history = []

    rewritten_query = await query_rewrite(query=payload.query, history=conversation_history)
    query = preprocess_query(rewritten_query)
    

    cached = get_cached_answer(query=query)
    if cached:
        try:
            if cached.lower()!="i don't have enough information to answer that question based on the provided documents" and "Error generating answer" not in  cached:
                await record_message(client_id=user_id, session_id=session_id, query=query, response=cached)
        except Exception as e:
            print(f"[history] failed to record cached response: {e}")
        print("cache hit")
        yield cached
        return

    try:
        chunks = await retriever.ainvoke(query)
    except AttributeError:
        chunks = retriever.invoke(query)
    answer_accum = ""

    async for token in generate_final_answer_stream(query=query, chunks=chunks, history=conversation_history):
        answer_accum += token
        yield token
        await asyncio.sleep(0)  # allow other tasks

    if answer_accum and answer_accum.lower()!="i don't have enough information to answer that question based on the provided documents." and "Error generating answer" not in answer_accum:
        store_cached_answer(query, answer_accum)
        try:
            await record_message(client_id=user_id, session_id=session_id, query=query, response=answer_accum)
        except Exception as e:
            print(f"[history] failed to record answer: {e}")


@app.post("/ask")
async def ask(payload: AskRequest):
    return StreamingResponse(stream_answer(payload), media_type="text/plain")


@app.get("/history")
async def history(user_id: str = "default", session_id: str = "default"):
    try:
        history = await fetch_history(session_id or user_id or "default")
    except Exception as e:
        print(f"[history] failed to fetch from db: {e}")
        history = []
    return {"history": history}

if __name__ == "__main__":
    # For production, use environment variable PORT (set by hosting platforms)
    port = int(os.environ.get("PORT", 8000))
    # Only enable reload in development
    reload = os.environ.get("ENVIRONMENT", "development") == "development"
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=reload)

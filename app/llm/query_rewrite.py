import json
from typing import List, Dict
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

def format_history_for_query(history: List[Dict[str, str]]) -> str:
    if not history:
        return "None"
    lines = []
    for turn in history:
        role = turn.get("role", "user")
        text = turn.get("text", "")
        prefix = "User" if role == "user" else "Bot"
        lines.append(f"{prefix}: {text}")
    return "\n".join(lines)

async def query_rewrite(query: str, history=None) -> str:
    """Rewrite a follow-up into a standalone question using chat history."""
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        rewrite_prompt = f"""
Rewrite the user's question so it stands alone, using the conversation for context.
Return only the rewritten question, nothing else.

Chat History:
{format_history_for_query(history)}

Question:
{query}

Standalone Question:
"""
        message = HumanMessage(content=[{"type": "text", "text": rewrite_prompt}])
        response = await llm.ainvoke([message])
        return response.content.strip()
    except Exception as e:
        return query  # fall back to the original question on error

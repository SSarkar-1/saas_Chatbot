import os
from typing import List, Dict

import asyncpg
from dotenv import load_dotenv

load_dotenv()

_pool: asyncpg.pool.Pool | None = None


async def get_pool() -> asyncpg.pool.Pool:
    """
    Lazily create and cache a connection pool for Neon/Postgres.
    """
    global _pool
    if _pool is None:
        database_url = os.getenv("NEON_DB_URL")
        if not database_url:
            raise RuntimeError("NEON_DB_URL not set")
        _pool = await asyncpg.create_pool(dsn=database_url, min_size=1, max_size=5)
    return _pool


async def record_message(client_id: str, session_id: str, query: str, response: str, keep: int = 4) -> None:
    """
    Insert a new Q&A pair and keep only the newest `keep` rows for this session.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO chat_history (client_id, session_id, query, response)
            VALUES ($1, $2, $3, $4)
            """,
            client_id,
            session_id,
            query,
            response,
        )
        await conn.execute(
            """
            DELETE FROM chat_history
            WHERE session_id = $1
              AND id NOT IN (
                SELECT id FROM chat_history
                WHERE session_id = $1
                ORDER BY created_at DESC
                LIMIT $2
              )
            """,
            session_id,
            keep,
        )


async def fetch_history(session_id: str, keep: int = 4) -> List[Dict[str, str]]:
    """
    Return interleaved user/bot messages for the most recent entries.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT query, response
            FROM chat_history
            WHERE session_id = $1
            ORDER BY created_at DESC
            LIMIT $2
            """,
            session_id,
            keep,
        )

    # Reverse to chronological order before interleaving
    messages: List[Dict[str, str]] = []
    for row in reversed(rows):
        messages.append({"role": "user", "text": row["query"]})
        messages.append({"role": "bot", "text": row["response"]})
    return messages

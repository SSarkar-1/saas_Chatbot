import json
import os
from typing import List, Dict

HISTORY_FILE = "conversation_history.json"


def _load() -> Dict[str, List[Dict[str, str]]]:
    if not os.path.exists(HISTORY_FILE):
        return {}
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def _save(data: Dict[str, List[Dict[str, str]]]) -> None:
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def append_history(user_id: str, question: str, answer: str) -> None:
    data = _load()
    history = data.get(user_id, [])
    history.append({"role": "user", "text": question})
    history.append({"role": "bot", "text": answer})
    data[user_id] = history[-50:]  # keep last 50 turns per user
    _save(data)


def get_history(user_id: str) -> List[Dict[str, str]]:
    data = _load()
    return data.get(user_id, [])

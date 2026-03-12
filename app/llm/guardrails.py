BANNED_TOPICS = [
    "politics",
    "violence",
    "illegal activity"
]

def check_query(query):

    for topic in BANNED_TOPICS:

        if topic in query.lower():
            raise ValueError("Query blocked by guardrails")

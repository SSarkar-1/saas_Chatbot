import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))
from fastapi import FastAPI
from app.retrieval.retriever import load_retriever
from app.llm.generator import generate_final_answer


query = "What is the formula for Scaled Dot-Product Attention?"

retriever=load_retriever()

chunks = retriever.invoke(query)
answer = generate_final_answer(query=query,chunks=chunks)
print(answer)
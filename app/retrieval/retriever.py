import json
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain.schema import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()
# ✅ Load the already-persisted Chroma DB directly



# def generate_final_answer(chunks, query):
#     """Generate final answer using multimodal content"""
#     db = Chroma(
#     persist_directory="vector_store/chroma_db",
#     embedding_function=OpenAIEmbeddings(model="text-embedding-3-small")
# )
    
#     try:
#         # Initialize LLM (needs vision model for images)
#         llm = ChatOpenAI(model="gpt-4o", temperature=0)
        
#         # Build the text prompt
#         prompt_text = f"""Based on the following documents, please answer this question: {query}

# CONTENT TO ANALYZE:
# """
        
#         for i, chunk in enumerate(chunks):
#             prompt_text += f"--- Document {i+1} ---\n"
            
#             if "original_content" in chunk.metadata:
#                 original_data = json.loads(chunk.metadata["original_content"])
                
#                 # Add raw text
#                 raw_text = original_data.get("raw_text", "")
#                 if raw_text:
#                     prompt_text += f"TEXT:\n{raw_text}\n\n"
                
#                 # Add tables as HTML
#                 tables_html = original_data.get("tables_html", [])
#                 if tables_html:
#                     prompt_text += "TABLES:\n"
#                     for j, table in enumerate(tables_html):
#                         prompt_text += f"Table {j+1}:\n{table}\n\n"
            
#             prompt_text += "\n"
        
#         prompt_text += """
# Please provide a clear, comprehensive answer using the text, tables, and images above. If the documents don't contain sufficient information to answer the question, say "I don't have enough information to answer that question based on the provided documents."

# ANSWER:"""

#         # Build message content starting with text
#         message_content = [{"type": "text", "text": prompt_text}]
        
#         # Add all images from all chunks
#         for chunk in chunks:
#             if "original_content" in chunk.metadata:
#                 original_data = json.loads(chunk.metadata["original_content"])
#                 images_base64 = original_data.get("images_base64", [])
                
#                 for image_base64 in images_base64:
#                     message_content.append({
#                         "type": "image_url",
#                         "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
#                     })
        
#         # Send to AI and get response
#         message = HumanMessage(content=message_content)
#         response = llm.invoke([message])
        
#         return response.content
        
#     except Exception as e:
#         print(f"❌ Answer generation failed: {e}")
#         return "Sorry, I encountered an error while generating the answer."

# # Usage
# # final_answer = generate_final_answer(chunks, query)
# # print(final_answer)
def load_retriever():

    db = Chroma(
        persist_directory="vector_store/chroma_db",
        embedding_function=OpenAIEmbeddings(model="text-embedding-3-small")
    )

    retriever = db.as_retriever(
        search_kwargs={"k": 3}
    )

    return retriever
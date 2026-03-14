import json
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI


async def generate_final_answer_stream(query, chunks):
    """Yield answer tokens as they stream from the OpenAI chat model."""
    try:
        llm = ChatOpenAI(model="gpt-4o", temperature=0, streaming=True)

        prompt_text = f"""Based on the following documents, please answer this question: {query}

CONTENT TO ANALYZE: """

        for i, chunk in enumerate(chunks):
            prompt_text += f"--- Document {i+1} ---\n"

            if "original_content" in chunk.metadata:
                original_data = json.loads(chunk.metadata["original_content"])

                raw_text = original_data.get("raw_text", "")
                if raw_text:
                    prompt_text += f"TEXT:\n{raw_text}\n\n"

                tables_html = original_data.get("tables_html", [])
                if tables_html:
                    prompt_text += "TABLES:\n"
                    for j, table in enumerate(tables_html):
                        prompt_text += f"Table {j+1}:\n{table}\n\n"

            prompt_text += "\n"

        prompt_text += """
Provide a clear, comprehensive,pointwise answer using the text, tables, and images above even(only test or images or tables may be present).Only if any of the documents don't have sufficient information (text or tables or images) to answer the question, say "I don't have enough information to answer that question based on the provided documents."

ANSWER:"""

        message_content = [{"type": "text", "text": prompt_text}]

        for chunk in chunks:
            if "original_content" in chunk.metadata:
                original_data = json.loads(chunk.metadata["original_content"])
                images_base64 = original_data.get("images_base64", [])

                for image_base64 in images_base64:
                    message_content.append(
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                        }
                    )

        message = HumanMessage(content=message_content)

        async for chunk in llm.astream([message]):
            if chunk.content:
                yield chunk.content

    except Exception as e:
        yield f"[Error generating answer: {e}]"

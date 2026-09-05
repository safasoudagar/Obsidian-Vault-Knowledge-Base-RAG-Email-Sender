import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_answer(question, retrieved_chunks):
    context_parts = []

    for i, chunk in enumerate(retrieved_chunks):
        context_parts.append(
            f"""
SOURCE {i + 1}
File: {chunk['source']}
Section: {chunk['heading_path']}

Content:
{chunk['text']}
"""
        )

    context = "\n".join(context_parts)

    prompt = f"""
You are an AI assistant that answers questions
using the user's Obsidian notes.

IMPORTANT RULES:

1. Use ONLY the information provided in the context.
2. Do not use your own outside knowledge.
3. Do not invent facts.
4. If the answer cannot be found in the context,
   say exactly:

   "I couldn't find this information in your Obsidian notes."

5. Answer clearly and concisely.
6. Do NOT include a Sources section.
7. Do NOT mention the source files in your answer.
8. Only answer using information supported by the context.

Context:
{context}

Question:
{question}

Answer:
"""

    response = client.chat.completions.create(
        model="qwen/qwen3.6-27b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_completion_tokens=300,
        reasoning_format="hidden",
    )

    return response.choices[0].message.content
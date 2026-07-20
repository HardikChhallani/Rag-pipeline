# generation/prompts.py

RAG_PROMPT_TEMPLATE = """
You are a helpful and intelligent assistant. You have been provided with context from a knowledge base.
Use the following pieces of context to answer the user's question.
If you don't know the answer based on the context, just say that you don't know, don't try to make up an answer.

--- CONTEXT ---
{context}

--- QUESTION ---
{question}

Answer:
"""

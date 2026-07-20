import google.generativeai as genai
from config import config
from .prompts import RAG_PROMPT_TEMPLATE

class LLMClient:
    def __init__(self):
        self.provider = config.llm_provider.lower()
        if self.provider == "gemini":
            if not config.gemini_api_key:
                print("WARNING: GEMINI_API_KEY is not set. Generation might fail if it requires auth.")
            genai.configure(api_key=config.gemini_api_key)
            self.model = genai.GenerativeModel(config.gemini_model_name)
        else:
            raise NotImplementedError(f"LLM Provider {self.provider} is not implemented yet. Set provider to 'gemini'.")

    def generate_answer(self, query: str, retrieved_contexts: list[str]) -> str:
        """Generates an answer using the provided contexts and query."""
        
        # Combine retrieved contexts into one string
        context_str = "\n\n".join([f"--- Context {i+1} ---\n{ctx}" for i, ctx in enumerate(retrieved_contexts)])
        
        # Build prompt
        prompt = RAG_PROMPT_TEMPLATE.format(context=context_str, question=query)
        
        if self.provider == "gemini":
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                return f"Error generating response: {e}"
        return "LLM Provider not configured properly."

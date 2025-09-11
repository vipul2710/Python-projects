# src/summarize/model_router.py
import textwrap
from typing import Dict, Callable
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load env file
load_dotenv()

class MockProvider:
    def complete(self, prompt: str, mode: str = "brief", category: str = "General") -> str:
        seed = textwrap.shorten(prompt, width=120, placeholder="...")
        if mode == "brief":
            return f"• {seed.split('.')[0]}\n• Monitor developments in {category.replace('_',' ')}."
        else:
            why = f"Why it matters: This may impact {category.replace('_',' ')} workflows."
            recs = "- Run a POC.\n- Track adoption impacts."
            return f"{why}\n\nRecommendations:\n{recs}"

class OpenAIProvider:
    def __init__(self, model="gpt-4o-mini"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in .env or environment")
        # strip any stray quotes or non-ASCII chars
        api_key = api_key.strip().replace("“", "").replace("”", "").replace('"', "")
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def complete(self, prompt: str, mode: str = "brief", category: str = "General") -> str:
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"You are a summarizer specializing in {category}."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print("❌ OpenAI error:", repr(e))
            raise

class ModelRouter:
    def __init__(self):
        self.providers: Dict[str, Callable] = {}
        self.register_provider("mock", MockProvider())
        self.register_provider("openai", OpenAIProvider())

    def register_provider(self, name: str, provider: Callable):
        self.providers[name] = provider

    def complete(self, prompt: str, provider: str = "mock", mode: str = "brief", category: str = "General") -> str:
        if provider not in self.providers:
            raise ValueError(f"Provider {provider} not registered.")
        return self.providers[provider].complete(prompt, mode=mode, category=category)

if __name__ == "__main__":
    router = ModelRouter()
    test_prompt = "AI is reshaping the analytics industry with automation and efficiency gains."

    def safe_print(label, text):
        try:
            print(f"{label}\n{text}")
        except UnicodeEncodeError:
            print(f"{label}\n{text.encode('utf-8', 'ignore').decode('utf-8')}")

    safe_print("Brief (mock):", router.complete(test_prompt, provider="mock", mode="brief", category="AI_ML_Analytics"))
    safe_print("Brief (openai):", router.complete(test_prompt, provider="openai", mode="brief", category="AI_ML_Analytics"))

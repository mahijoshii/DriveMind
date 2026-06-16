from abc import ABC, abstractmethod
import re

from app.config import get_settings
from app.models.schemas import Citation

settings = get_settings()


class AIProvider(ABC):
    @abstractmethod
    def answer(self, question: str, citations: list[Citation]) -> str:
        raise NotImplementedError


class DummyAIProvider(AIProvider):
    def answer(self, question: str, citations: list[Citation]) -> str:
        if not citations:
            return "I could not find indexed Drive content related to that question yet."
        usable = [citation for citation in citations if citation.score > 0.08]
        if not usable:
            return "I found indexed documents, but none matched the question strongly. Try using a more specific keyword that appears in your Docs."
        top = usable[:3]
        lines = []
        for citation in top:
            sentence = re.split(r"(?<=[.!?])\s+", citation.excerpt.strip())[0]
            lines.append(f"- {citation.document_title}: {sentence}")
        return "Here is what I found in your indexed Drive docs:\n" + "\n".join(lines)


class OpenAIProvider(AIProvider):
    def answer(self, question: str, citations: list[Citation]) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        context = "\n\n".join(f"Source: {c.document_title}\nExcerpt: {c.excerpt}" for c in citations)
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Answer only from the supplied excerpts. If unsure, say what is missing. Cite sources by title."},
                {"role": "user", "content": f"Question: {question}\n\nExcerpts:\n{context}"},
            ],
        )
        return res.choices[0].message.content or ""


class GeminiProvider(AIProvider):
    def answer(self, question: str, citations: list[Citation]) -> str:
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        context = "\n\n".join(f"Source: {c.document_title}\nExcerpt: {c.excerpt}" for c in citations)
        res = model.generate_content(f"Answer from these excerpts only.\nQuestion: {question}\n\n{context}")
        return res.text


def get_ai_provider() -> AIProvider:
    provider = settings.ai_provider.lower()
    if provider == "openai":
        return OpenAIProvider()
    if provider == "gemini":
        return GeminiProvider()
    return DummyAIProvider()

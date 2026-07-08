from abc import ABC, abstractmethod
import re

from app.config import get_settings
from app.models.schemas import Citation

settings = get_settings()

SUMMARY_WORDS = {"summarize", "summary", "overview", "key", "main", "important", "explain"}
ACTION_WORDS = {"action", "actions", "item", "items", "todo", "todos", "follow", "followup", "follow-up", "next"}
DATE_WORDS = {"date", "dates", "deadline", "deadlines", "due", "when"}
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "i", "in",
    "is", "it", "of", "on", "or", "that", "the", "this", "to", "was", "with",
}


def tokens(text: str) -> list[str]:
    return [token for token in re.findall(r"[a-zA-Z0-9']+", text.lower()) if token not in STOPWORDS]


def split_sentences(text: str) -> list[str]:
    return [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", text) if len(sentence.strip()) > 35]


def top_sentences(text: str, limit: int = 4) -> list[str]:
    sentences = split_sentences(text)
    if not sentences:
        return [text.strip()[:260]] if text.strip() else []
    frequencies = {}
    for token in tokens(text):
        frequencies[token] = frequencies.get(token, 0) + 1
    ranked = []
    for index, sentence in enumerate(sentences):
        score = sum(frequencies.get(token, 0) for token in tokens(sentence))
        score = score / max(1, len(tokens(sentence)))
        ranked.append((score, index, sentence))
    selected = sorted(ranked, key=lambda item: item[0], reverse=True)[:limit]
    return [sentence for _, _, sentence in sorted(selected, key=lambda item: item[1])]


def focused_sentences(text: str, keywords: set[str], limit: int = 4) -> list[str]:
    matches = [sentence for sentence in split_sentences(text) if set(tokens(sentence)) & keywords]
    return matches[:limit] if matches else top_sentences(text, limit)


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
        question_terms = set(tokens(question))
        one_document = len({citation.document_title for citation in usable}) == 1
        combined_text = " ".join(citation.excerpt for citation in usable)
        if one_document and question_terms & SUMMARY_WORDS:
            bullets = top_sentences(combined_text, limit=4)
            return "Summary of this document:\n" + "\n".join(f"- {sentence}" for sentence in bullets)
        if one_document and question_terms & ACTION_WORDS:
            bullets = focused_sentences(combined_text, ACTION_WORDS, limit=4)
            return "Action items or next steps I found:\n" + "\n".join(f"- {sentence}" for sentence in bullets)
        if one_document and question_terms & DATE_WORDS:
            bullets = focused_sentences(combined_text, DATE_WORDS, limit=4)
            return "Dates or deadlines I found:\n" + "\n".join(f"- {sentence}" for sentence in bullets)
        top = usable[:3]
        lines = []
        for citation in top:
            sentence = re.split(r"(?<=[.!?])\s+", citation.excerpt.strip())[0]
            lines.append(f"- {citation.document_title}: {sentence}")
        if len({citation.document_title for citation in top}) == 1:
            return "Here is the strongest context from this document:\n" + "\n".join(lines)
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

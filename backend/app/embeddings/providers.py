import hashlib
import json
import math
import re
from abc import ABC, abstractmethod

from app.config import get_settings

settings = get_settings()


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class DummyEmbeddingProvider(EmbeddingProvider):
    stopwords = {
        "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "how", "i",
        "in", "is", "it", "me", "my", "of", "on", "or", "that", "the", "this", "to",
        "was", "what", "when", "where", "which", "who", "why", "with", "you", "your",
    }

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = []
        for text in texts:
            vec = [0.0 for _ in range(settings.embedding_dim)]
            tokens = [token for token in re.findall(r"[a-zA-Z0-9']+", text.lower()) if token not in self.stopwords]
            for token in tokens:
                idx = int(hashlib.sha256(token.encode()).hexdigest(), 16) % settings.embedding_dim
                vec[idx] += 1.0
            for first, second in zip(tokens, tokens[1:]):
                phrase = f"{first} {second}"
                idx = int(hashlib.sha256(phrase.encode()).hexdigest(), 16) % settings.embedding_dim
                vec[idx] += 1.5
            norm = math.sqrt(sum(v * v for v in vec)) or 1
            vectors.append([v / norm for v in vec])
        return vectors


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def embed(self, texts: list[str]) -> list[list[float]]:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        res = client.embeddings.create(model="text-embedding-3-small", input=texts, dimensions=settings.embedding_dim)
        return [item.embedding for item in res.data]


class GeminiEmbeddingProvider(EmbeddingProvider):
    def embed(self, texts: list[str]) -> list[list[float]]:
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        vectors = []
        for text in texts:
            res = genai.embed_content(model="models/text-embedding-004", content=text)
            vectors.append(res["embedding"])
        return vectors


def get_embedding_provider() -> EmbeddingProvider:
    provider = settings.embedding_provider.lower()
    if provider == "openai":
        return OpenAIEmbeddingProvider()
    if provider == "gemini":
        return GeminiEmbeddingProvider()
    return DummyEmbeddingProvider()


def dumps_vector(vector: list[float]) -> str:
    return json.dumps(vector)


def loads_vector(value: str) -> list[float]:
    return json.loads(value)

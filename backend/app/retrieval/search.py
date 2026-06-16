import math
import re

from sqlalchemy.orm import Session

from app.embeddings.providers import get_embedding_provider, loads_vector
from app.models.db import Chunk

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "how", "i",
    "in", "is", "it", "me", "my", "of", "on", "or", "that", "the", "this", "to",
    "was", "what", "when", "where", "which", "who", "why", "with", "you", "your",
}


def cosine(a: list[float], b: list[float]) -> float:
    denom = (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))) or 1
    return sum(x * y for x, y in zip(a, b)) / denom


def tokenize(text: str) -> list[str]:
    return [token for token in re.findall(r"[a-zA-Z0-9']+", text.lower()) if token not in STOPWORDS]


def lexical_score(question: str, chunk: Chunk) -> float:
    query_terms = tokenize(question)
    if not query_terms:
        return 0.0
    content = f"{chunk.document.title} {chunk.content}".lower()
    content_terms = set(tokenize(content))
    matches = sum(1 for term in query_terms if term in content_terms)
    phrase_boost = sum(1 for first, second in zip(query_terms, query_terms[1:]) if f"{first} {second}" in content)
    title_boost = sum(1 for term in query_terms if term in chunk.document.title.lower())
    raw = matches + (phrase_boost * 1.5) + (title_boost * 0.75)
    return min(1.0, raw / max(1, len(query_terms)))


def retrieve_chunks(db: Session, user_id: int, question: str, limit: int = 5) -> list[tuple[Chunk, float]]:
    query_vector = get_embedding_provider().embed([question])[0]
    chunks = db.query(Chunk).filter(Chunk.user_id == user_id).all()
    scored = []
    for chunk in chunks:
        vector_score = max(0.0, cosine(query_vector, loads_vector(chunk.embedding_json)))
        keyword_score = lexical_score(question, chunk)
        scored.append((chunk, (keyword_score * 0.65) + (vector_score * 0.35)))
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:limit]


def best_excerpt(question: str, content: str, max_chars: int = 520) -> str:
    terms = set(tokenize(question))
    sentences = re.split(r"(?<=[.!?])\s+", content)
    if not terms or not sentences:
        return content[:max_chars]
    ranked = []
    for sentence in sentences:
        sentence_terms = set(tokenize(sentence))
        ranked.append((len(terms & sentence_terms), sentence))
    ranked.sort(key=lambda item: item[0], reverse=True)
    excerpt = " ".join(sentence for score, sentence in ranked[:3] if score > 0).strip()
    if not excerpt:
        excerpt = content[:max_chars]
    return excerpt[:max_chars]

import math
import re
from collections import Counter

from sqlalchemy.orm import Session

from app.config import get_settings
from app.embeddings.providers import get_embedding_provider, loads_vector
from app.models.db import Chunk

settings = get_settings()

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "how", "i",
    "in", "is", "it", "me", "my", "of", "on", "or", "that", "the", "this", "to",
    "was", "what", "when", "where", "which", "who", "why", "with", "you", "your",
}

BROAD_DOCUMENT_TERMS = {
    "summarize", "summary", "overview", "explain", "action", "actions", "item",
    "items", "todo", "todos", "deadline", "deadlines", "date", "dates",
    "decision", "decisions", "follow", "followup", "follow-up", "important",
    "main", "key", "notes",
}


def cosine(a: list[float], b: list[float]) -> float:
    denom = (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))) or 1
    return sum(x * y for x, y in zip(a, b)) / denom


def tokenize(text: str) -> list[str]:
    return [token for token in re.findall(r"[a-zA-Z0-9']+", text.lower()) if token not in STOPWORDS]


def is_broad_document_question(question: str) -> bool:
    return bool(set(tokenize(question)) & BROAD_DOCUMENT_TERMS)


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


def bm25_scores(question: str, chunks: list[Chunk]) -> dict[int, float]:
    query_terms = tokenize(question)
    if not query_terms or not chunks:
        return {}

    tokenized_docs = {chunk.id: tokenize(f"{chunk.document.title} {chunk.content}") for chunk in chunks}
    avg_len = sum(len(tokens) for tokens in tokenized_docs.values()) / max(1, len(tokenized_docs))
    doc_freq = Counter()
    for tokens in tokenized_docs.values():
        doc_freq.update(set(tokens))

    scores: dict[int, float] = {}
    k1 = 1.6
    b = 0.72
    for chunk in chunks:
        tokens = tokenized_docs[chunk.id]
        counts = Counter(tokens)
        doc_len = len(tokens) or 1
        score = 0.0
        for term in query_terms:
            if counts[term] == 0:
                continue
            idf = math.log(1 + (len(chunks) - doc_freq[term] + 0.5) / (doc_freq[term] + 0.5))
            denom = counts[term] + k1 * (1 - b + b * (doc_len / max(1, avg_len)))
            score += idf * ((counts[term] * (k1 + 1)) / denom)
        title = chunk.document.title.lower()
        for first, second in zip(query_terms, query_terms[1:]):
            if f"{first} {second}" in title or f"{first} {second}" in chunk.content.lower():
                score += 1.25
        score += sum(0.75 for term in query_terms if term in title)
        scores[chunk.id] = score
    return scores


def retrieve_chunks(db: Session, user_id: int, question: str, limit: int = 5, document_id: int | None = None) -> list[tuple[Chunk, float]]:
    query_vector = get_embedding_provider().embed([question])[0]
    query = db.query(Chunk).filter(Chunk.user_id == user_id)
    if document_id is not None:
        query = query.filter(Chunk.document_id == document_id)
    chunks = query.all()
    bm25 = bm25_scores(question, chunks)
    scored = []
    for chunk in chunks:
        vector_score = max(0.0, cosine(query_vector, loads_vector(chunk.embedding_json)))
        keyword_score = lexical_score(question, chunk)
        bm25_score = bm25.get(chunk.id, 0.0)
        if settings.embedding_provider.lower() == "dummy":
            raw_score = (bm25_score * 0.8) + (keyword_score * 2.0)
        else:
            raw_score = (bm25_score * 0.55) + (keyword_score * 1.25) + (vector_score * 1.5)
        scored.append((chunk, raw_score))
    scored.sort(key=lambda item: item[1], reverse=True)
    useful = [item for item in scored if item[1] > 0][:limit]
    if document_id is not None and (not useful or is_broad_document_question(question)):
        ordered = sorted(chunks, key=lambda item: item.position)
        if len(ordered) <= limit:
            ordered_chunks = ordered
        else:
            step = max(1, len(ordered) // limit)
            ordered_chunks = ordered[::step][:limit]
        return [(chunk, max(0.42, 0.82 - (index * 0.08))) for index, chunk in enumerate(ordered_chunks)]
    if not useful:
        return []
    top_score = useful[0][1] or 1
    normalized = [(chunk, min(0.98, max(0.05, score / top_score))) for chunk, score in useful]
    return normalized


def best_excerpt(question: str, content: str, max_chars: int = 520) -> str:
    terms = set(tokenize(question))
    sentences = re.split(r"(?<=[.!?])\s+", content)
    if is_broad_document_question(question):
        excerpt = " ".join(sentence.strip() for sentence in sentences[:3] if sentence.strip())
        return (excerpt or content)[:max_chars]
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

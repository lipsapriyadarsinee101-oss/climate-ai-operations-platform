from dataclasses import dataclass
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class Chunk:
    source: str
    text: str
    score: float = 0


class LocalRetriever:
    """Local reference implementation; production boundary can use pgvector/Qdrant."""

    def __init__(self, knowledge_dir: str = "knowledge"):
        self.chunks = [
            Chunk(path.name, part.strip())
            for path in Path(knowledge_dir).glob("*.md")
            for part in path.read_text().split("\n\n")
            if part.strip()
        ]
        texts = [chunk.text for chunk in self.chunks] or ["empty"]
        self.vectorizer = TfidfVectorizer(stop_words="english").fit(texts)
        self.matrix = self.vectorizer.transform(texts)

    def search(self, query: str, top_k: int = 3) -> list[Chunk]:
        scores = cosine_similarity(self.vectorizer.transform([query]), self.matrix)[0]
        order = scores.argsort()[::-1][:top_k]
        return [Chunk(self.chunks[i].source, self.chunks[i].text, float(scores[i])) for i in order]

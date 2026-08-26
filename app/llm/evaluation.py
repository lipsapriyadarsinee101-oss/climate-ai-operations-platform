import re


def evaluate_answer(
    question: str, answer: str, contexts: list[str], latency_ms: float
) -> dict[str, float]:
    def tokenize(value: str) -> set[str]:
        return set(re.findall(r"[a-z0-9]+", value.lower()))

    answer_terms, question_terms = tokenize(answer), tokenize(question)
    context_terms = tokenize(" ".join(contexts))
    groundedness = len(answer_terms & context_terms) / max(1, len(answer_terms))
    relevance = len(answer_terms & question_terms) / max(1, len(question_terms))
    return {
        "groundedness": round(groundedness, 3),
        "question_relevance": round(relevance, 3),
        "latency_score": round(max(0, 1 - latency_ms / 5000), 3),
    }

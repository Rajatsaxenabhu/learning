def recall_at_k(
    retrieved_sources: list[str],
    relevant_sources: set[str],
    k: int,
) -> float:

    retrieved = set(
        retrieved_sources[:k]
    )

    if not relevant_sources:
        return 0.0

    return len(
        retrieved & relevant_sources
    ) / len(relevant_sources)


def precision_at_k(
    retrieved_sources: list[str],
    relevant_sources: set[str],
    k: int,
) -> float:

    retrieved = retrieved_sources[:k]

    if not retrieved:
        return 0.0

    relevant_count = sum(
        source in relevant_sources
        for source in retrieved
    )

    return relevant_count / len(retrieved)


def hit_rate_at_k(
    retrieved_sources: list[str],
    relevant_sources: set[str],
    k: int,
) -> float:

    retrieved = set(
        retrieved_sources[:k]
    )

    return float(
        bool(retrieved & relevant_sources)
    )


def reciprocal_rank(
    retrieved_sources: list[str],
    relevant_sources: set[str],
) -> float:

    for rank, source in enumerate(
        retrieved_sources,
        start=1,
    ):
        if source in relevant_sources:
            return 1.0 / rank

    return 0.0
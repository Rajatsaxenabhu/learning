from app.api.service.rag.evaluation.metrics import (
    recall_at_k,
    precision_at_k,
    hit_rate_at_k,
    reciprocal_rank,
)


async def evaluate_rag(
    rag,
    dataset,
    k: int = 5,
):

    results = []

    for item in dataset:

        query = item["query"]

        relevant_sources = set(
            item["relevant_sources"]
        )

        result = await rag.run(
            query=query,
            candidate_k=15,
            k=k,
        )

        retrieved_sources = [
            doc.metadata.get("source", "")
            for doc in result[
                "retrieved_documents"
            ]
        ]

        recall = recall_at_k(
            retrieved_sources,
            relevant_sources,
            k,
        )

        precision = precision_at_k(
            retrieved_sources,
            relevant_sources,
            k,
        )

        hit_rate = hit_rate_at_k(
            retrieved_sources,
            relevant_sources,
            k,
        )

        mrr = reciprocal_rank(
            retrieved_sources,
            relevant_sources,
        )

        results.append(
            {
                "query": query,
                "recall": recall,
                "precision": precision,
                "hit_rate": hit_rate,
                "mrr": mrr,
                "retrieved_sources": retrieved_sources,
            }
        )

    return results

async def evaluate_memory(self, state):

    documents = state["candidate_documents"]

    if not documents:
        return {
            "retrieval_sufficient": False,
            "missing_information": "No relevant information found.",
            "evaluation_reason": "Qdrant returned no relevant documents.",
            "status": "memory_insufficient",
        }

    evaluation = await self.evaluator.evaluate(
        query=state["query"],
        documents=documents,
    )

    if evaluation["sufficient"]:
        return {
            "retrieved_documents": documents,
            "retrieval_sufficient": True,
            "missing_information": "",
            "evaluation_reason": evaluation["reason"],
            "status": "memory_sufficient",
        }

    return {
        "retrieved_documents": documents,
        "retrieval_sufficient": False,
        "missing_information": evaluation["missing_information"],
        "evaluation_reason": evaluation["reason"],
        "status": "memory_insufficient",
    }

    



def after_memory_evaluation(state):
    if state["retrieval_sufficient"]:
        return "generate"

    return "search"


def after_search(state):
    status = state["status"]

    if status == "searched":
        return "extract"

    if status in {"no_search_results", "search_failed"}:
        if state["search_retry_count"] < state["max_search_retries"]:
            return "retry_search"

        return "fail"

    return "fail"


def after_extract(state):
    if state["status"] == "extracted":
        return "chunk"

    return "fail"


def after_chunk(state):
    if state["status"] == "chunked":
        return "retrieve"

    return "fail"


def after_retrieve(state):
    if state["status"] == "retrieved":
        return "rerank"

    return "refine"


def after_rerank(state):
    if state["status"] == "reranked":
        return "evaluate"

    return "refine"


def after_evaluation(state):
    if state["retrieval_sufficient"]:
        return "generate"

    if state["iteration"] >= state["max_iterations"]:
        return "generate"

    if not state["missing_information"].strip():
        return "generate"

    return "refine"


def after_refine(state):
    if state["status"] == "duplicate_query":
        return "fail"

    if state["iteration"] >= state["max_iterations"]:
        return "generate"

    return "search"


def after_generate(state):
    if state["status"] == "invalid_citations":
        return "repair_citations"

    return "end"


def after_repair(state):
    if state["status"] == "success":
        return "end"

    return "fail"

def after_freshness(state):

    if state["force_web_search"]:
        return "search"

    if state["freshness_required"]:
        return "search"

    return "memory"


def after_memory_evaluation(state):

    if state["retrieval_sufficient"]:
        return "generate"

    return "search"
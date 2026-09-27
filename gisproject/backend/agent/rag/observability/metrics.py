from time import perf_counter


class RAGMetrics:

    @staticmethod
    def start():
        return perf_counter()

    @staticmethod
    def elapsed_ms(start):
        return round(
            (perf_counter() - start) * 1000,
            2,
        )

    @staticmethod
    def update(
        state,
        key,
        value,
    ):
        metrics = {
            **state.get("metrics", {}),
            key: value,
        }

        return {
            "metrics": metrics,
        }
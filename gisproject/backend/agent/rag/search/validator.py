import re


class CitationValidator:

    CITATION_PATTERN = re.compile(r"\[(\d+)\]")

    def validate(
        self,
        answer: str,
        sources: list[dict],
    ) -> dict:
        """
        Validate citations in a generated RAG answer.
        """

        valid_ids = {
            str(source["id"])
            for source in sources
        }

        citations = self.CITATION_PATTERN.findall(answer)

        invalid_citations = [
            citation
            for citation in citations
            if citation not in valid_ids
        ]

        return {
            "valid": len(invalid_citations) == 0,
            "citations": citations,
            "invalid_citations": invalid_citations,
        }
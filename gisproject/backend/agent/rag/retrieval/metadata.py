from datetime import datetime, timezone
import hashlib

from langchain_core.documents import Document


class DocumentMetadata:

    @staticmethod
    def content_hash(content: str) -> str:
        return hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()

    @staticmethod
    def add(
        document: Document,
        fetched_at: str | None = None,
    ) -> Document:

        if fetched_at is None:
            fetched_at = datetime.now(
                timezone.utc
            ).isoformat()

        content_hash = DocumentMetadata.content_hash(
            document.page_content
        )

        document.metadata.update(
            {
                "fetched_at": fetched_at,
                "content_hash": content_hash,
            }
        )

        return document
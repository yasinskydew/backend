from abc import ABC, abstractmethod


class StorageProvider(ABC):
    """Abstract interface for object storage backends."""

    @abstractmethod
    async def upload(
        self,
        *,
        object_key: str,
        data: bytes,
        content_type: str,
    ) -> str:
        """Upload object and return etag (without surrounding quotes)."""

    @abstractmethod
    async def delete(self, *, object_key: str) -> None:
        """Delete object. Missing keys (404) must be treated as success."""

    @abstractmethod
    def build_public_url(self, object_key: str) -> str:
        """Return a publicly accessible URL for the object key."""

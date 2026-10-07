from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ObjectHeadResult:
    """Metadata returned by a successful HEAD on a stored object."""

    size: int
    etag: str | None
    content_type: str | None


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

    @abstractmethod
    async def create_presigned_put_url(
        self,
        *,
        object_key: str,
        content_type: str,
        expires_in: int,
    ) -> str:
        """Return a time-limited PUT URL for direct client upload."""

    @abstractmethod
    async def head_object(self, *, object_key: str) -> ObjectHeadResult | None:
        """Return object metadata, or None if the key does not exist."""

from qdrant_client import AsyncQdrantClient

from medibot.common import config, IntegrationClient


class QdrantDBClient(IntegrationClient):
    client: AsyncQdrantClient

    async def close(self) -> None:
        await self.client.close()
        super().close()

    def init(self) -> None:
        self.client = AsyncQdrantClient(url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY or None)


qdrant_db_client = QdrantDBClient()

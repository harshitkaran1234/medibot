from medibot.common import IntegrationClient, logger
from .qdrant_db_client import qdrant_db_client


class Dependency(IntegrationClient):

    async def init(self):
        logger.info("Initializing dependencies")
        qdrant_db_client.init()

    async def close(self):
        logger.info("Closing all dependencies")
        await qdrant_db_client.close()


dependency = Dependency()

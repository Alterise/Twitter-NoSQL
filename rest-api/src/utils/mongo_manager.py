import os
from typing import Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


db_client: AsyncIOMotorClient


class MongoDBManager:

    @staticmethod
    async def init_mongo_client(mongo_uri: str = str(os.getenv('MONGO_URL')),
                                mongo_db: str = str(os.getenv('MONGO_DB'))):
        global db_client
        try:
            db_client = AsyncIOMotorClient(mongo_uri)
            await db_client.server_info()
            print(f'Connected to mongo with uri {mongo_uri}')
            if mongo_db not in await db_client.list_database_names():
                db_client.get_database(mongo_db)
                print(f'Database {mongo_db} created')
        except Exception as ex:
            print(f'Cant connect to mongo: {ex}')

    @staticmethod
    async def get_db() -> AsyncIOMotorDatabase:
        global db_client
        mongo_db_name: str = str(os.getenv('MONGO_DB'))
        return AsyncIOMotorDatabase(db_client, name=mongo_db_name)

    @staticmethod
    def close_connection():
        global db_client
        db_client.close() if db_client else None

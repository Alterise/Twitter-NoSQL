from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from repositories.mongo.mongodb import MongoDBCollection
from utils.mongo_manager import MongoDBManager
import os


class MongoUsersCollection(MongoDBCollection):
    def __init__(self, db: AsyncIOMotorDatabase, db_collection: AsyncIOMotorCollection):
        super().__init__(db, db_collection)

    @staticmethod
    async def get_instance(mongo_db: AsyncIOMotorDatabase = Depends(MongoDBManager.get_db)):
        collection_name: str = "users"
        collection_names = await mongo_db.list_collection_names()
        if collection_name not in collection_names:
            await mongo_db.create_collection(name=collection_name)
        db_collection: AsyncIOMotorCollection = mongo_db[collection_name]
        return MongoUsersCollection(db=mongo_db, db_collection=db_collection)

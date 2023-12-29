import json
from pydoc import doc
from typing import Sequence
import os
from elasticsearch import AsyncElasticsearch
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
import asyncio
from copy import deepcopy


async def load(collection: str):
    # Считываем файл
    file_path = os.path.join(os.path.abspath(
        os.path.dirname(__file__)), f'{collection}.json')
    with open(file_path, "r", encoding='utf-8') as json_file:
        json_data: list[dict] = json.load(json_file)[:50_000]
        print(f"Json with len {len(json_data)} was loaded")

    # Подключаемся к mongo и сохраняем данные
    mongoURI = ['mongodb://localhost:27017',
                'localhost:27018',
                'localhost:27019']
    db_client = AsyncIOMotorClient(mongoURI)
    try:
        await db_client.server_info()
        print(f'Connected to mongo with uri {mongoURI}')
    except Exception as e:
        print(e)
    db_client.get_database("api-db")

    mongoDB: AsyncIOMotorDatabase = AsyncIOMotorDatabase(
        db_client, name="api-db")
    collection_names = await mongoDB.list_collection_names()
    if collection not in collection_names:
        await mongoDB.create_collection(name=collection)
    mongoCollection: AsyncIOMotorCollection = mongoDB[collection]
    chunk_size = 5000
    mongoData = deepcopy(json_data)
    mongoChunks = [mongoData[i:i + chunk_size]
                   for i in range(0, len(mongoData), chunk_size)]
    inserted_ids = []
    for i in range(len(mongoChunks)):
        inserted_info = await mongoCollection.insert_many(mongoChunks[i])
        inserted_ids += list(map(str, inserted_info.inserted_ids))
        print(f"Chunk {i} inserted to mongo")
    print("Inserted to mongo")

    # Подключаемся к elastic и сохраняем данные
    elasticsearch_URI = "http://localhost:9200,http://localhost:9201,http://localhost:9202"
    elasticsearch_hosts: Sequence = elasticsearch_URI.split(',')

    elasticsearch_client = AsyncElasticsearch(elasticsearch_hosts)
    print(f'Connected to elasticsearch with uri {elasticsearch_URI}')

    bulk = []
    for i in range(len(json_data)):
        index_operation = {
            'index': {'_index': collection, '_id': inserted_ids[i]}}
        bulk.append(index_operation)
        bulk.append(json_data[i])

    chunks = [bulk[i:i + chunk_size]
              for i in range(0, len(bulk), chunk_size)]
    for i in range(len(chunks)):
        await elasticsearch_client.bulk(operations=chunks[i])
        print(f"Chunk {i} of added")
    print("Added to elastic")
    await elasticsearch_client.close()


async def main():
    await load('tweets')
    await load('users')
asyncio.run(main=main())

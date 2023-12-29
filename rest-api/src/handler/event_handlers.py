import asyncio

from utils.memcached_utils import MemcachedManager
from utils.mongo_manager import MongoDBManager
from utils.elasticsearch_utils import ElsaticSearchManager


async def startup():
    init_mongo_future = MongoDBManager.init_mongo_client()
    init_elasticsearch_future = ElsaticSearchManager.connect_and_init_elasticsearch()
    await asyncio.gather(init_mongo_future, init_elasticsearch_future)
    MemcachedManager.init_memcached_client()


async def shutdown():
    MongoDBManager.close_connection()
    MemcachedManager.close_memcached_connect()
    await ElsaticSearchManager.close_elasticsearch_connect()

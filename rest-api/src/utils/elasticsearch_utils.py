import os
from typing import Sequence
from elasticsearch import AsyncElasticsearch

elasticsearch_client: AsyncElasticsearch


class ElsaticSearchManager:

    @staticmethod
    async def connect_and_init_elasticsearch():
        global elasticsearch_client
        elasticsearch_url = str(os.getenv('ELASTICSEARCH_URL'))
        elasticsearch_hosts: Sequence = elasticsearch_url.split(',')
        try:
            elasticsearch_client = AsyncElasticsearch(elasticsearch_hosts)
            print(f'Connected to elasticsearch with uri {elasticsearch_url}')
        except Exception as ex:
            print(f'Cant connect to elasticsearch: {ex}')

    @staticmethod
    def get_elasticsearch_client() -> AsyncElasticsearch:
        global elasticsearch_client
        return elasticsearch_client

    @staticmethod
    async def close_elasticsearch_connect():
        global elasticsearch_client
        if elasticsearch_client is None:
            return
        await elasticsearch_client.close()

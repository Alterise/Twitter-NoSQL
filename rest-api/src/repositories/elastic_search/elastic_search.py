from typing import Any, Mapping, Sequence
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from pydantic import BaseModel


class ElasticSearch:
    _elasticsearch_client: AsyncElasticsearch
    _elasticsearch_index: str

    def __init__(self, index: str, elasticsearch_client: AsyncElasticsearch):
        self._elasticsearch_client = elasticsearch_client
        self._elasticsearch_index = index

    async def create(self, obj_id: str, obj: Mapping[str, Any]):
        await self._elasticsearch_client.create(index=self._elasticsearch_index, id=obj_id, document=obj)

    async def update(self, obj_id: str, obj):
        await self._elasticsearch_client.update(index=self._elasticsearch_index, id=obj_id, doc=dict(obj))

    async def delete(self, obj_id: str):
        await self._elasticsearch_client.delete(index=self._elasticsearch_index, id=obj_id)

    async def find_by_atr(self, atr: str, description: str):
        index_exist = await self._elasticsearch_client.indices.exists(index=self._elasticsearch_index)
        if not index_exist:
            return []
        query = {
            "fuzzy": {
                atr: {
                    "value": description
                }
            }
        }
        scroll_time = "10m"
        response = await self._elasticsearch_client.search(index=self._elasticsearch_index, query=query, scroll=scroll_time)
        if 'hits' not in response.body:
            return {}
        total = int(response['hits']['total']['value'])
        scroll_id = response['_scroll_id']
        hits = response.body['hits']['hits']
        result = [hit['_source'] for hit in hits]
        response = {
            "hits": result,
            "scroll_id": scroll_id,
            "total": int(total)
        }
        return response

    async def find_by_dates(self, first_date: int, second_date: int):
        index_exist = await self._elasticsearch_client.indices.exists(index=self._elasticsearch_index)
        if not index_exist:
            return []
        query = {
            "bool": {
                "must": [
                    {"range": {"created_at": {"gte": first_date}}},
                    {"range": {"created_at": {"lte": second_date}}}
                ]
            }
        }
        scroll_time = "10m"
        response = await self._elasticsearch_client.search(index=self._elasticsearch_index, query=query, scroll=scroll_time)
        if 'hits' not in response.body:
            return [], ""
        total = int(response['hits']['total']['value'])
        scroll_id = response['_scroll_id']
        hits = response.body['hits']['hits']
        for hit in hits:
            hit['_source']['id'] = hit['_id']
        result = [hit['_source'] for hit in hits]
        response = {
            "hits": result,
            "scroll_id": scroll_id,
            "total": int(total)
        }
        return response

    async def scroll(self, scroll_id: str):
        scroll_time = "10m"
        response = await self._elasticsearch_client.scroll(scroll=scroll_time, scroll_id=scroll_id)
        if 'hits' not in response.body:
            return [], ""
        scroll_id = response['_scroll_id']
        hits = response.body['hits']['hits']
        for hit in hits:
            hit['_source']['id'] = hit['_id']
        result = [hit['_source'] for hit in hits]
        total = int(response['hits']['total']['value'])
        response = {
            "hits": result,
            "scroll_id": scroll_id,
            "total": int(total)
        }
        return response

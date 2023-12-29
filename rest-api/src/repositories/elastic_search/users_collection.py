from fastapi import Depends
import os
from elasticsearch import AsyncElasticsearch
from repositories.elastic_search.elastic_search import ElasticSearch
from utils.elasticsearch_utils import ElsaticSearchManager


class ElasticUsersCollection(ElasticSearch):
    def __init__(self, index: str, elasticsearch_client: AsyncElasticsearch):
        super().__init__(index, elasticsearch_client)

    @staticmethod
    def get_instance(elasticsearch_client: AsyncElasticsearch = Depends(ElsaticSearchManager.get_elasticsearch_client)):
        elasticsearch_index: str = "users"
        return ElasticUsersCollection(elasticsearch_index, elasticsearch_client)

from collections.abc import Generator

from elasticsearch import Elasticsearch

es_client = Elasticsearch("http://localhost:9200")

def get_es_client() -> Generator[Elasticsearch, None, None]:
    yield es_client

from elasticsearch import Elasticsearch

es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}]).options(
    request_timeout=30,
    max_retries=10,
    retry_on_timeout=True
)

response = es.indices.delete(index='transcripts', ignore=[400, 404])
print("Index 'transcripts' deleted if it existed.")
print(response)

"""BM25 retrieval using Elasticsearch."""
from typing import Dict, List, Union

from ccc.utils.es.index.index import ElasticsearchIndex


class BM25Retriever:
    def __init__(
        self,
        index: ElasticsearchIndex,
        fields: List[str] = ["body"],
        k1: float = 1.2,
        b: float = 0.75,
    ) -> None:
        """Initializes BM25 retrieval model based on Elasticsearch.

        Args:
            index: ElasticSearch index.
            fields: Index fields to query.
            k1: BM25 parameter. Defaults to 1.2.
            b: BM25 parameter. Defaults to 0.75.
        """
        self._index = index
        self._index.update_similarity_parameters(k1=k1, b=b)
        self._fields = fields

    def retrieve(
        self, query: str, page: int = 1, num_results: int = 10
    ) -> List[Dict]:
        """Performs retrieval.

        Args:
            query: Query.
            page: Page number. Defaults to 1.
            num_results: Number of documents to return. Defaults to 10.

        Returns:
            Retrieved documents.
        """

        res = self._index.es.search(
            body={
                "query": {
                    "multi_match": {"query": query, "fields": self._fields}
                }
            },
            index=self._index.index_name,
            _source=True,
            size=num_results,
            from_=(page - 1) * num_results,
        )

        documents = list()
        for hit in res["hits"]["hits"]:
            doc = {"doc_id": hit["_id"]}
            doc.update(hit["_source"])
            documents.append(doc)

        return documents


def create_retriever(
    index_params: Dict, retriever_params: Union[Dict, None] = None
) -> BM25Retriever:
    """Instantiates a BM25 retriever based on Elasticsearch.

    See BaseConfig class for an example of parameters.

    Args:
        index_params: Parameters to instantiate Elasticsearch index.
        retriever_params: Parameters to instantiate BM25 retriever.

    Returns:
        Retriever.
    """
    if "index_name" not in index_params:
        raise RuntimeError(
            "The parameter dictionary for the Elasticsearch index"
            " must have the key index_name."
        )

    es_index = ElasticsearchIndex(**index_params)
    if retriever_params:
        return BM25Retriever(es_index, **retriever_params)

    return BM25Retriever(es_index)

"""Interface for Elasticsearch."""
from typing import Dict, List

from ccc import config
from ccc.utils.es.bm25_retriever import create_retriever


def init_elasticsearch(env: str) -> None:
    """Initializes the Elasticsearch interface regarding the environment."""
    global es_retriever_cast
    global es_retriever_product

    app_config = config.get_config(env)
    # TREC CAsT index
    index_params_cast = app_config.ES_INDEX_CAST
    retriever_params_cast = app_config.ES_RETRIEVER_CAST
    es_retriever_cast = create_retriever(
        index_params_cast, retriever_params_cast
    )


def search_trec(query: str, page: int = 1, num_results=10) -> List[Dict]:
    """Retrieves TREC CAsT passages.

    Args:
        query: Query.
        page: Page number. Defaults to 1.
        num_results: Number of results to retrieve.

    Returns:
        List of product matching with the query.
    """
    return es_retriever_cast.retrieve(query, page=page, num_results=num_results)

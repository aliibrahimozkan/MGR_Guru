import pandas as pd

from index_inverter import IndexInverter
from helpers import BM25Parameters
class ModelWithoutQueryExpansion:
    def __init__(self, restaurants_data: pd.DataFrame, bm25_parameters: BM25Parameters):
        """
        IR Model that computes Document Relevance based on Query
        :param restaurants_data: Corpus
        :param bm25_parameters: Okapi BM25 parameters (k1 and b)
        """
        self.index_inverter = IndexInverter(restaurants_data= restaurants_data, bm25_parameters=bm25_parameters)

    def sort_documents(self, query:str) -> list:
        """
        Sort Documents based on a given Query
        :param query: Query given by User
        :return: Sorted Document ID List
        """
        stemmed_query_terms = [self.index_inverter.stem_word(word) for word in query.split() if self.index_inverter.check_stop_word(word)]
        hits = self.index_inverter.search_query_term(stemmed_query_terms)
        return [hit.dict()['__id__'] for hit in hits]

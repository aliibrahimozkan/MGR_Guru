
from index_inverter import IndexInverter
from helpers import BM25Parameters
from gensim.models import Word2Vec
from gensim.models import KeyedVectors
import numpy as np
import pandas as pd
class ModelWithEmbedQueryExpansion:
    def __init__(self, restaurants_data: pd.DataFrame, bm25_parameters: BM25Parameters,
                 embedding_model_path: str):
        """
        IR Model that computes Document Relevance based on Query

        :param restaurants_data: Corpus
        :param bm25_parameters: Okapi BM25 parameters (k1 and b)
        :param embedding_model_path: Pretrained word2vec model path
        """

        self.index_inverter = IndexInverter(restaurants_data= restaurants_data, bm25_parameters=bm25_parameters)
        try:
            self.embed_model = KeyedVectors.load_word2vec_format(embedding_model_path, binary=True)
        except:
            self.embed_model = KeyedVectors.load(embedding_model_path).wv

        # Similarity threshold
        self.embed_similarity_thr = 0.6
        self.max_expansion_words = 5


    def sort_documents(self, query:str) -> list:
        """
        Sort Documents based on a given Query
        :param query: Query given by User
        :return: Sorted Document ID List
        """
        stemmed_query_terms = [self.index_inverter.stem_word(word) for word in query.split() if self.index_inverter.check_stop_word(word)]

        # Find most similar terms
        similar_terms_above_threshold = []
        query_terms_without_stop_words = [word for word in query.split() if self.index_inverter.check_stop_word(word)]
        for term in query_terms_without_stop_words:
            similar_terms = self.embed_model.most_similar(term)

            term_above_threshold = []
            for word, similarity in similar_terms:
                if similarity >= self.embed_similarity_thr:
                    if '_' in word:
                        split_list = word.split('_')
                        term_above_threshold.extend(split_list)
                    else:
                        term_above_threshold.append(word)

            if len(term_above_threshold) > self.max_expansion_words:
                term_above_threshold = term_above_threshold[:self.max_expansion_words]

            similar_terms_above_threshold.extend(term_above_threshold)
        expanded_terms = [self.index_inverter.stem_word(word) for word in similar_terms_above_threshold if self.index_inverter.check_stop_word(word)]

        expanded_terms = list(set(expanded_terms))
        stemmed_query_terms.extend(expanded_terms)
        stemmed_query_terms = list(np.unique(np.array(stemmed_query_terms)))
        hits = self.index_inverter.search_query_term(stemmed_query_terms)

        return [hit.dict()['__id__'] for hit in hits]

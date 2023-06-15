import pandas as pd

from index_inverter import IndexInverter
from helpers import BM25Parameters
from gensim.models import Word2Vec
from gensim.models import KeyedVectors
from gensim.utils import simple_preprocess
from scipy.spatial.distance import cosine
import numpy as np

class MGRGuru:
    def __init__(self, restaurants_data:pd.DataFrame , bm25_parameters: BM25Parameters,
                 embedding_model_path: str):
        """
        IR Model that computes Document Relevance based on Query
        :param restaurants_data: Corpus
        :param bm25_parameters: Okapi BM25 parameters (k1 and b)
        :param embedding_model_path: Pretrained word2vec model path
        """

        self.index_inverter = IndexInverter(restaurants_data = restaurants_data, bm25_parameters=bm25_parameters)
        try:
            self.embed_model = KeyedVectors.load_word2vec_format(embedding_model_path, binary=True)
        except:
            self.embed_model = KeyedVectors.load(embedding_model_path).wv

        self.previous_query_clicked_links = {}

        # Similarity threshold
        self.embed_similarity_thr = 0.6
        self.query_similarity_thr = 0.7
        self.max_expansion_words = 5


    def sort_documents(self, query: str) -> list:
        """
        Sort Documents based on a given Query
        :param query: Query given by User
        :return: Sorted Document ID List
        """

        stemmed_query_terms = [self.index_inverter.stem_word(word) for word in query.split()
                               if self.index_inverter.check_stop_word(word)]

        # Find Most Similar Terms
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

        # Find Most Similar Queries and Clicked Document IDs
        highest_tf_idf_terms_from_prev_clicks = []
        clicked_doc_ids = self.identify_relevant_past_queries_clicked_doc_ids(query)
        for doc_id in clicked_doc_ids:
            highest_tf_idf_terms_from_prev_clicks.extend(self.index_inverter.determine_highest_tf_idf_terms_in_document(doc_id))

        # Query Expansion and Ranking
        expanded_terms = list(set(expanded_terms))
        stemmed_query_terms.extend(expanded_terms)
        stemmed_query_terms.extend(highest_tf_idf_terms_from_prev_clicks)
        stemmed_query_terms = list(np.unique(np.array(stemmed_query_terms)))
        hits = self.index_inverter.search_query_term(stemmed_query_terms)
        return [hit.dict()['__id__'] for hit in hits]

    def identify_relevant_past_queries_clicked_doc_ids(self, query:str) -> list:
        """
        Determine the Previous Queries that Similar to the Current Query
        and determine Clicked Document IDs
        :param query: Given Query
        :return: Clicked Document Links
        """

        max_similarity = -1000
        most_similar_prev_query = ""
        query = ' '.join([word for word in query.split() if self.index_inverter.check_stop_word(word)])

        # Determine Most Similar Previous Query
        for previous_query, clicked_docs in self.previous_query_clicked_links.items():
            # Preprocess Query and Previous Query
            tokens1 = simple_preprocess(query)
            tokens2 = simple_preprocess(previous_query)

            # Calculate the Sentence Vectors
            sentence_vec_1 = self.embed_model[tokens1].mean(axis=0)
            sentence_vec_2 = self.embed_model[tokens2].mean(axis=0)
            query_similarity = 1 - cosine(sentence_vec_1, sentence_vec_2)
            if query_similarity > max_similarity:
                max_similarity = query_similarity
                most_similar_prev_query = previous_query

        # Determine Clicked Documents
        clicked_docs =[]
        if max_similarity > self.query_similarity_thr:
            clicked_docs = self.previous_query_clicked_links[most_similar_prev_query]
        return clicked_docs

    def store_query_clicked_doc_id(self, previous_query:str, previous_clicked_doc_ids:list):
        """
        Store the Query-Clicked Documents Pair
        :param previous_query: Previous Query
        :param previous_clicked_doc_ids: Previous Documents that Clicked
        :return: None
        """
        query_terms_without_stop_words = [word for word in previous_query.split() if self.index_inverter.check_stop_word(word)]
        query_terms_without_stop_words = ' '.join(query_terms_without_stop_words)

        if query_terms_without_stop_words in self.previous_query_clicked_links:
            self.previous_query_clicked_links[query_terms_without_stop_words].extend(previous_clicked_doc_ids)
        else:
            self.previous_query_clicked_links[query_terms_without_stop_words] = previous_clicked_doc_ids


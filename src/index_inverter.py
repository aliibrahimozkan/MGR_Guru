from lupyne import engine
import math
import pandas as pd
import numpy as np
import lucene
from org.apache.lucene.search.similarities import BM25Similarity
import shutil
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import nltk
nltk.download('stopwords')
from helpers import BM25Parameters

class IndexInverter:
    def __init__(self, restaurants_data:pd.DataFrame, bm25_parameters: BM25Parameters):
        """
        Store & Search Engine based on Java Lucene
        :param restaurants_data: Corpus
        :param bm25_parameters: Okapi BM25 parameters (k1 and b)
        """
        lucene.initVM()

        self.index_path_name = 'temp'
        self.bm25_parameters = bm25_parameters
        self.indexer = engine.Indexer(self.index_path_name)
        self.searcher = None

        # Initialize Stemmer, Stop Word Model and Store Documents to Lucene Directory
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        self.store_restaurants_content(restaurants_data)



    def store_restaurants_content(self, restaurants_data):
        """
        Store Documents, Terms to Lucene Directory
        :param restaurants_data: Our Corpus
        :return: None
        """

        # Set Indexer Field Names
        self.indexer.set('name', stored=True)
        self.indexer.set('content', engine.Field.Text, stored=True, storeTermVectors=True)

        # Add Document to Index After Preprocessing
        for name, content in zip(np.array(restaurants_data['Name']), np.array(restaurants_data['Data'].astype(str))):
            stemmed_content = ' '.join([self.stem_word(word) for word in content.split() if self.check_stop_word(word)])
            self.indexer.add(name=name, content=stemmed_content)

        # Commit writes and refresh searcher
        self.indexer.commit()

        # Set Searcher BM25 Similarity Configuration
        self.searcher = engine.IndexSearcher(self.index_path_name)
        self.searcher.setSimilarity(BM25Similarity(self.bm25_parameters.k1, self.bm25_parameters.b))


    def search_query_term(self, query_terms:list):
        """
        Search the Multi Term Query with Lucene Searcher and Retrieved Sorted Documents
        :param query_terms: Terms List in Given Query
        :return: Sorted Document
        """
        query = engine.Query.any(*[engine.Query.term('content', term) for term in query_terms])
        hits = self.searcher.search(query, scores=True)  # run search and return sequence of documents
        return hits
    def determine_highest_tf_idf_terms_in_document(self, document_id:int):
        """
        Determine the Terms with Highest TF/IDF in Given Document
        :param document_id: Restaurant ID
        :return: Terms with Highest TF/IDF  List
        """
        terms_with_tf = self.searcher.termvector(document_id, 'content',counts=True)
        document_num = self.searcher.numDocs()

        terms, tf_idf_values = [], []
        for term, freq in terms_with_tf:
            document_count = self.searcher.count('content:' + term)
            if document_count > 1:
                idf = math.log(document_num / document_count)
                tf_idf = freq * idf
                tf_idf_values.append(tf_idf)
                terms.append(term)

        sorted_indexes = sorted(range(len(tf_idf_values)), key=lambda i: tf_idf_values[i], reverse=True)
        if len(sorted_indexes) > 5:
            sorted_indexes = sorted_indexes[:5]

        return np.array(terms)[sorted_indexes]

    def delete_directory(self):
        """
        Deleting the Lucene Directory that Stores Documents
        :return: None
        """
        shutil.rmtree(self.index_path_name)

    def check_stop_word(self, word:str) -> bool:
        """
        Controlling Word is Stop Word or Not
        :param word: Query Term
        :return: False if word is stop word
        """
        return True if word not in self.stop_words else False

    def stem_word(self, word:str):
        """
        Stemming the Word
        :param word: Query Term
        :return: Stemmed Word
        """
        return self.stemmer.stem(word)
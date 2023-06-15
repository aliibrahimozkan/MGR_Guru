import sys

from PyQt5 import uic
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QDialog, QVBoxLayout, QListWidget, QTextBrowser
from PyQt5.QtGui import QTextCursor
import pandas as pd
from helpers import BM25Parameters, remove_punctuation
import urllib.parse
import argparse
import csv
import os

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--model_name', default="mgr_guru",
                        type=str, help='IR Model Name (mgr_guru, supp_model_1 or supp_model_2)')

    parser.add_argument('--data_path', default="../data/restaurant_corpus.csv", type=str, help='Corpus path')

    parser.add_argument('--embedding_model_path', default= "../models/GoogleNews-vectors-negative300.bin",
                        type=str, help='word2vec model path')

    parser.add_argument('--bm25_parameters', default=[1.2, 0.75], type=list, help='Okapi BM25 parameters (k1 and b)')
    args = parser.parse_args()
    return args

class MainWindow(QMainWindow):
    def __init__(self,model_name:str , data_path:str , embedding_model_path:str, bm25_parameters:BM25Parameters):
        """
        Main API that accepts query
        :param model_name: IR Model Name
        :param data_path: path of the document data
        :param bm25_parameters: Okapi BM25 parameters (k1 and b)
        """

        super().__init__()

        self.model_name = model_name
        self.restaurant_details = pd.read_csv(data_path, dtype=str)
        self.query = None
        self.max_number_of_restaurants_in_UI = 10

        # API initialization
        ui = "Main.ui"
        self.ui = uic.loadUi(ui, self)
        self.setWindowTitle("MGR-Guru")
        self.searchButton.clicked.connect(self.step) # connect signal to slot
        self.second_window = ResultWindow()
        self.queries_list = []

        # Query-Result Saving
        is_result_file_exist = os.path.exists('../data/query_results.csv')
        self.csv_file = open('../data/query_results.csv', 'a', newline='')
        self.writer = csv.writer(self.csv_file)
        if not is_result_file_exist:
            self.writer.writerow(['Model Name', 'Query Number', 'Query', 'Model Result', 'Ranking'])
        self.model_name = model_name

        # Model Initialization
        if model_name == "mgr_guru":
            from mgr_guru_model import MGRGuru
            self.ranking_model = MGRGuru(restaurants_data=self.restaurant_details ,bm25_parameters=bm25_parameters,
                                         embedding_model_path=embedding_model_path)
        elif model_name == "supp_model_1":
            from supplementer_model_1 import ModelWithoutQueryExpansion
            self.ranking_model = ModelWithoutQueryExpansion(restaurants_data=self.restaurant_details ,bm25_parameters=bm25_parameters)
        elif model_name == "supp_model_2":
            from supplementer_model_2 import ModelWithEmbedQueryExpansion
            self.ranking_model = ModelWithEmbedQueryExpansion(restaurants_data=self.restaurant_details, bm25_parameters=bm25_parameters,
                                                              embedding_model_path=embedding_model_path)
        else:
            print("Model Name is Invalid! Valid IR Model Names are 'mgr_guru', 'supp_model_1', 'supp_model_2'")

    def step(self):
        """
        Main function for Calling Ranking Model & Showing Result
        :return: None
        """
        self.second_window.delete_results()

        # Storing Previous Query & Clicked Doc. IDs
        if self.query is not None and self.model_name == 'mgr_guru':
            previous_query = self.query
            previous_clicked_doc_id = self.second_window.get_clicked_doc_id()
            if len(previous_clicked_doc_id) > 0:
                self.ranking_model.store_query_clicked_doc_id(previous_query, previous_clicked_doc_id)
                self.second_window.delete_clicked_links()

        self.query = remove_punctuation(self.queryText.toPlainText())
        # Calling Document Ranking Model and Get Sorted Document IDs
        documents_id = self.ranking_model.sort_documents(self.query)
        if len(documents_id) > self.max_number_of_restaurants_in_UI:
            documents_id = documents_id[:self.max_number_of_restaurants_in_UI]
        print(documents_id)

        # Showing Sorted Documents
        self.second_window.addResult(" ", " ",
                                     f"Here are {len(documents_id)} restaurants found based on the given query.","")
        self.queries_list.append(self.query)
        query_no = self.queries_list.count(self.query)
        for i, id in enumerate(documents_id):
            restaurant = self.restaurant_details.iloc[id]
            self.writer.writerow([self.model_name, query_no, self.query ,restaurant['Name'], i+1])
            self.second_window.addResult(restaurant['Name'], restaurant['Link'], restaurant['Content'], id)

        self.second_window.resultBrowser.moveCursor(QTextCursor.Start)
        self.second_window.show()

    def closeEvent(self, event):
        """
        API Windows Closing Event
        :param event: clicking close button
        :return: None
        """
        self.ranking_model.index_inverter.delete_directory()
        self.csv_file.close()
        event.accept()

class ResultWindow(QDialog):
    def __init__(self):
        """
        Results API that shows sorted documents
        """
        super(ResultWindow, self).__init__()
        self.clicked_doc_id = []
        self.url_doc_id_pairs = {}

        # UI initialization
        ui = "Results.ui"
        self.ui = uic.loadUi(ui, self)
        self.setWindowTitle("MGR-Guru Results")
        self.resultBrowser.anchorClicked.connect(self.log_clicked_link)  # connect signal to slot


    def delete_results(self):
        """
        Deleting sorted documents result
        :return: None
        """
        self.resultBrowser.clear()

    def addResult(self, title, url, intro, document_id=None):
        """
        Adding documents to UI window
        :param title: Restaurant name
        :param url: Restaurant URL
        :param intro: Restaurant Short Introduction
        :param document_id: Restaurant ID
        :return: None
        """
        if document_id is not None:
            url_updated_for_turkish_chars = urllib.parse.unquote(url)
            self.url_doc_id_pairs[url_updated_for_turkish_chars] = document_id
        self.resultBrowser.append(
            f"<div style='width: 400px; margin: 20px;'><h2><a href='{url}'>{title}</a></h2>{intro}<hr></div>")

    def log_clicked_link(self,url):
        """
        Log the Links that User Clicks
        :param url: Restaurant URL
        :return: None
        """
        self.clicked_doc_id.append(self.url_doc_id_pairs[url.url()])
        QDesktopServices.openUrl(url)  # open URL in a browser

    def delete_clicked_links(self):
        """
        Delete Stored Clicked Logs
        :return:None
        """
        self.clicked_doc_id = []
    def get_clicked_doc_id(self):
        """
        Getter for Clicked Document ID
        :return: Clicked Document ID
        """
        return self.clicked_doc_id


if __name__ == '__main__':
    args = get_args()
    app = QApplication(sys.argv)
    window = MainWindow(model_name=args.model_name, data_path=args.data_path,
                        embedding_model_path=args.embedding_model_path,
                        bm25_parameters=BM25Parameters(k1=args.bm25_parameters[0], b=args.bm25_parameters[1]))
    window.show()
    sys.exit(app.exec())

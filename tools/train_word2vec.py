import argparse
import re
import nltk
from nltk.corpus import stopwords
from gensim.models import Word2Vec
import numpy as np
import pandas as pd


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--pretrained_model_path", type=str, default="../GoogleNews-vectors-negative300.bin",
                        help="Path of the default Word2Vec model.")
    parser.add_argument("--corpus_path", type=str, default="../data/restaurant_corpus.csv",
                        help="Path of the csv file which contains list of restaurants and their reviews.")
    parser.add_argument("--train_epochs", type=int, default=10,
                        help="Number of epochs the training algorithm will run.")
    parser.add_argument("--result_model_path", type=str, default="../models/pretrained_Word2Vec.bin",
                        help="Path to which resulting pre-trained model wil be saved.")

    args = parser.parse_args()
    return args


def preprocess_text(text: str):
    """
    Preprocess text data. Remove '...More's, numeric and special characters, and tokenize.
    """
    text = re.sub(r"...More", "", text)
    text = re.sub(r"\n", " ", text)
    text = re.sub(r"[^A-Za-z]+", " ", text)
    tokens = nltk.word_tokenize(text)
    tokens = [w.lower().strip() for w in tokens]
    return tokens


def main():
    args = get_args()

    # Read corpus, omit NaN values
    corpus = pd.read_csv(args.corpus_path)
    corpus = corpus.loc[corpus["Data"].notna()]
    print("Corpus size: {}".format(corpus.size))

    # Download stopwords and punkt
    nltk.download("stopwords")
    nltk.download("punkt")

    # Preprocess
    corpus["Cleaned"] = corpus.Data.apply(lambda x: preprocess_text(x))
    txtDataList = corpus.Cleaned.tolist()

    # Fine-tune GoogleNews Word2Vec vectors
    model = Word2Vec(vector_size=300, sg=1)
    model.build_vocab(txtDataList)
    print("Number of words in corpora: {}".format(len(model.wv)))
    model.wv.vectors_lockf = np.ones(len(model.wv), dtype=np.float32)
    model.wv.intersect_word2vec_format(args.pretrained_model_path, lockf=1.0, binary=True)
    model.train(txtDataList, total_examples=len(txtDataList), epochs=10)
    model.save(args.result_model_path)


if __name__ == "__main__":
    main()

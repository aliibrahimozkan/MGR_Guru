
import pandas as pd
import argparse

def merge_restaurant_data_and_reviews(michelin_guide_data_path: str, tripadvisor_restaurant_reviews_paths:list,
                                      out_corpus_path: str):
    """
    Merge Michelin Guide Data and TripAdvisor Reviews & Generate Corpus
    :param michelin_guide_data_path: Michelin Guide Data
    :param tripadvisor_restaurant_reviews_paths: TripAdvisor Restaurant Reviews
    :param out_corpus_path: Corpus Data Saving Path
    :return:
    """
    michelin_guide_data = pd.read_csv(michelin_guide_data_path)

    # Read Trip Advisor Reviews
    tripadvisor_reviews = []
    for review_path in tripadvisor_restaurant_reviews_paths:
        review = pd.read_csv(review_path, sep="½", dtype = str)
        review = review.drop('Unnamed: 0', axis=1)
        tripadvisor_reviews.append(review)

    merged_tripadvisor_reviews = pd.concat(tripadvisor_reviews)
    for column in merged_tripadvisor_reviews.columns:
        merged_tripadvisor_reviews[column] = merged_tripadvisor_reviews[column].astype(str)

    merged_tripadvisor_reviews = merged_tripadvisor_reviews.groupby('Name').agg(' '.join).reset_index()
    restaurant_corpus = pd.merge(michelin_guide_data, merged_tripadvisor_reviews, on='Name', how='outer')

    # Merge Michelin Guide Data and Reviews
    restaurant_corpus['Data'] = restaurant_corpus['Content'] +\
                                restaurant_corpus['Detail'] + \
                                restaurant_corpus['Title'].fillna('-') + \
                                restaurant_corpus['Text'].fillna('-')


    # Remove Unnecessary Columns
    unnecessary_columns = ['User', 'Date', 'Hour', 'Detail', 'Services', 'Title', 'Text' ]
    for column in unnecessary_columns:
        restaurant_corpus = restaurant_corpus.drop(column, axis=1)
    restaurant_corpus.to_csv(out_corpus_path)


def main(args):
    merge_restaurant_data_and_reviews(michelin_guide_data_path=args.restaurant_michelin_data_path,
                                      tripadvisor_restaurant_reviews_paths=args.restaurant_tripadvisor_reviews_path,
                                      out_corpus_path=args.out_corpus_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--restaurant_michelin_data_path', default="../data/restaurants_details.csv",
                        type=str, help='Michelin Site Restaurant Data')

    parser.add_argument('--restaurant_tripadvisor_reviews_path',
                        default=["../data/restaurant_reviews.csv",
                                 "../data/restaurant_reviews_1.csv",
                                 "../data/restaurant_reviews_2.csv",
                                 "../data/restaurant_reviews_3.csv",
                                 "../data/restaurant_reviews_4.csv",
                                 "../data/restaurant_reviews_5.csv"],
                        type=list, help='TripAdvisor Restaurant Reviews')

    parser.add_argument('--out_corpus_path', default="../data/restaurant_corpus.csv",
                        type=str, help='Output Corpus Path')

    args = parser.parse_args()
    main(args)

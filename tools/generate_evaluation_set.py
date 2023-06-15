
import pandas as pd
import numpy as np
import argparse

char_mappings = {
    'ı': 'i',
    'ğ': 'g',
    'ü': 'u',
    'ş': 's',
    'ö': 'o',
    'ç': 'c',
    'İ': 'I',
    'Ğ': 'G',
    'Ü': 'U',
    'Ş': 'S',
    'Ö': 'O',
    'Ç': 'C'
}

def generate_evaluation_set(michelin_guide_data_path: str,
                            tripadvisor_restaurant_reviews_paths:list, out_evaluation_set_path: str):
    """
    Generate Manually Labelled Evaluation Set
    :param michelin_guide_data_path: Michelin Guide Data
    :param tripadvisor_restaurant_reviews_paths: TripAdvisor Restaurant Reviews
    :param out_evaluation_set_path: Evaluation Data Saving Path
    :return:
    """
    michelin_guide_data = pd.read_csv(michelin_guide_data_path)
    tripadvisor_reviews = []
    for review_path in tripadvisor_restaurant_reviews_paths:
        review = pd.read_csv(review_path, sep="½", dtype = str)
        review = review.drop('Unnamed: 0', axis=1)
        tripadvisor_reviews.append(review)

    merged_tripadvisor_reviews = pd.concat(tripadvisor_reviews)
    for column in merged_tripadvisor_reviews.columns:
        merged_tripadvisor_reviews[column] = merged_tripadvisor_reviews[column].astype(str)

    ## Manually Labelled for Terrace, Wine Menu and Vegetarian Menu
    merged_tripadvisor_reviews = merged_tripadvisor_reviews.groupby('Name').agg(' '.join).reset_index()
    evaluation_set = pd.merge(michelin_guide_data, merged_tripadvisor_reviews, on='Name', how='outer')
    evaluation_set['Cuisine Type'] = evaluation_set['Content'].str.split(r'[\n·]').apply(lambda x: x[-1])
    evaluation_set['Expensiveness'] = evaluation_set['Content'].str.split(r'[\n·]').apply(lambda x: len(x[-2]))
    evaluation_set['Country'] = evaluation_set['Content'].str.split(r'[\n·]').apply(lambda x: x[1].split(r',')[-1])
    evaluation_set['Country'] = evaluation_set['Country'].apply(lambda x: x.replace(" ", ""))
    evaluation_set['Country'] = evaluation_set['Country'].str.replace(r'[ığıüşöçİĞÜŞÖÇ]', lambda m: char_mappings[m.group()], regex=True)
    evaluation_set['Country'] = evaluation_set['Country'].apply(lambda x: x.replace("Turkiye", "Turkey"))

    evaluation_set['Rating'] = evaluation_set['Rating'].fillna(0)
    evaluation_set['Rating'] = evaluation_set['Rating'].astype(str)
    evaluation_set['Rating'] = evaluation_set['Rating'].apply(lambda x: np.fromstring(x, sep=' '))
    evaluation_set['Mean Rating'] = evaluation_set['Rating'].apply(lambda x: np.mean(x))
    evaluation_set['Terrace Available'] = evaluation_set['Services'].apply(lambda x: 'Terrace' in x)
    evaluation_set['Vegetarian Menu Available'] = evaluation_set['Services'].apply(lambda x: 'vegetarian' in x or 'Vegetarian' in x)
    evaluation_set['Wine Menu Available'] = evaluation_set['Services'].apply(lambda x: 'wine' in x or 'Wine' in x)

    # Remove Unnecessary Columns
    unnecessary_columns = ['User', 'Date', 'Hour', 'Detail', 'Services', 'Title', 'Text', 'Rating','Content', 'Link']
    for column in unnecessary_columns:
        evaluation_set = evaluation_set.drop(column, axis=1)
    evaluation_set.to_csv(out_evaluation_set_path, index=False)


def main(args):
    generate_evaluation_set(michelin_guide_data_path=args.restaurant_michelin_data_path,
                                      tripadvisor_restaurant_reviews_paths=args.restaurant_tripadvisor_reviews_path,
                                      out_evaluation_set_path=args.out_evaluation_set_path)


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

    parser.add_argument('--out_evaluation_set_path', default="../data/evaluation_set.csv",
                        type=str, help='Output Evaluation Path')

    args = parser.parse_args()
    main(args)

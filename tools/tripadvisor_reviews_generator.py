import argparse
import pandas as pd

from utils.tripadvisor_site_driver import TripadvisorSiteDriver


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--restaurants_path", type=str, default="../data/restaurants_list.csv",
                        help="Path of the csv file which contains lis of restaurants.")
    parser.add_argument("--num_pages_per_item", type=int, default=10, help="Number of review pages per restaurant.")
    parser.add_argument("--results_path", type=str, default="../data/ratings_reviews.csv",
                        help="Path of the csv file in which ratings and reviews will be saved.")

    args = parser.parse_args()
    return args


def __read_restaurants_list(restaurants_path: str):
    """
    Reads names and locations of the restaurants from the given csv file.
    """
    restaurants = pd.read_csv(restaurants_path)
    restaurant_names = restaurants["Name"].tolist()
    restaurant_links = restaurants["Link"].tolist()
    restaurant_locations = []

    for i in range(len(restaurant_names)):
        curLink = restaurant_links[i]
        curLocation = curLink.split("/")[-3]
        restaurant_locations.append(curLocation)

    return [restaurant_names, restaurant_locations]


def generate_restaurant_reviews(site_driver: TripadvisorSiteDriver, restaurant_names: str, restaurant_locations: str, \
                                num_pages_per_restaurant: int, output_results_path: str):
    """
    Generate Review&Rating Data from TripAdvisor
    :param site_driver: Chrome Driver
    :param restaurant_names: Restaurant Name
    :param restaurant_locations: Restaurant Links
    :param num_pages_per_restaurant: Trip Advisor Resturants Page Number
    :param output_results_path: Data save folder path
    :return:
    """
    first_result_written = False
    for i in range(len(restaurant_names)):
        reviews_ratings_df_curRestaurant = pd.DataFrame(columns=["Name", "Title", "User", "Date", "Rating", "Text"])
        curName = restaurant_names[i]
        curLocation = restaurant_locations[i]
        review_titles, review_users, review_dates, review_ratings, review_texts = \
            site_driver.get_reviews_ratings(restaurant_name=curName, restaurant_location=curLocation,
                                            num_pages=num_pages_per_restaurant)
        for j in range(len(review_titles)):
            reviews_ratings_df_curRestaurant = reviews_ratings_df_curRestaurant.append({
                "Name": curName,
                "Title": review_titles[j],
                "User": review_users[j],
                "Date": review_dates[j],
                "Rating": review_ratings[j],
                "Text": review_texts[j]
            }, ignore_index=True)
        if not first_result_written:
            reviews_ratings_df_curRestaurant.to_csv(output_results_path, sep="½")
            first_result_written = True
        else:
            reviews_ratings_df_curRestaurant.to_csv(output_results_path, mode="a", header=False, sep="½")


def main():

    args = get_args()

    site_driver = TripadvisorSiteDriver()
    site_driver.open_driver()

    # Read restaurant names and locations from CSV
    restaurant_names, restaurant_locations = __read_restaurants_list(args.restaurants_path)

    # Get reviews and ratings for each restaurant and write them to CSV file
    generate_restaurant_reviews(site_driver=site_driver, restaurant_names=restaurant_names, restaurant_locations=restaurant_locations, \
        num_pages_per_restaurant=args.num_pages_per_item, output_results_path=args.results_path)

    site_driver.close_driver()


if __name__ == "__main__":
    main()

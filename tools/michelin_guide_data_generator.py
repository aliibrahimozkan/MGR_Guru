
import sys
from utils.michelin_guide_site_driver import MichelinGuideSiteDriver
import pandas as pd
import numpy as np
import argparse
import os

def generate_restaurant_list(site_driver: MichelinGuideSiteDriver, output_folder_path: str):
    """
    Generate whole restaurant list in Michelin Guide Site
    :param site_driver: Chrome Driver
    :param output_folder_path: Data save folder path
    :return: Restaurants
    """
    number_of_pages_in_site = 809
    number_of_restaurant_in_a_page = 20
    number_of_restaurant_in_last_page = 20

    restaurant_names, restaurant_links = np.empty(0), np.empty(0)
    for page in range(1, number_of_pages_in_site + 1):
        restaurant_num = number_of_restaurant_in_a_page
        if page == number_of_pages_in_site - 1:
            restaurant_num = number_of_restaurant_in_last_page

        names_in_page, links_in_page = site_driver.get_michelin_restaurants_list(page, restaurant_num)
        restaurant_names = np.append(restaurant_names, names_in_page)
        restaurant_links = np.append(restaurant_links, links_in_page)

    restaurant_list = pd.DataFrame({'Name': restaurant_names, 'Link': restaurant_links})
    restaurant_list.to_csv(os.path.join(output_folder_path, 'restaurants_list.csv'), index=False)
    return restaurant_list


def generate_restaurant_details_document(site_driver: MichelinGuideSiteDriver, restaurant_list: pd.DataFrame,
                                         output_folder_path: str):
    """
    Generate Restaurant Details from Michelin Guide Website
    :param site_driver: Chrome Driver
    :param restaurant_list: List of the Restaurants in Michelin Guide
    :param output_folder_path: Data save folder path
    :return:
    """
    restaurant_names, restaurant_links = np.array(restaurant_list['Name']), np.array(restaurant_list['Link'])
    restaurants_details, restaurants_services, restaurants_open_hours, restaurants_contents = [], [], [], []

    for i, (name, link) in enumerate(zip(restaurant_names, restaurant_links)):
        restaurant_content, restaurant_detail, restaurant_service, restaurant_open_hour = site_driver.get_michelin_restaurant_data(
            link)

        restaurants_details.append(restaurant_detail)
        restaurants_services.append(restaurant_service)
        restaurants_open_hours.append(restaurant_open_hour)
        restaurants_contents.append(restaurant_content)

    restaurants_details = pd.DataFrame({'Name': restaurant_names, 'Link': restaurant_links,
                                        'Content': restaurants_contents, 'Detail': restaurants_details,
                                        'Services': restaurants_services, 'Hour': restaurants_open_hours})
    restaurants_details.to_csv(os.path.join(output_folder_path, 'restaurants_details.csv'), index=False)


def main(args):
    site_driver = MichelinGuideSiteDriver(args.chrome_driver_path)
    site_driver.open_driver()
    restaurant_list = generate_restaurant_list(site_driver, args.output_folder_path)
    generate_restaurant_details_document(site_driver, restaurant_list, args.output_folder_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--chrome_driver_path', default="/home/ibrahim/Downloads/chromedriver_linux64_new/chromedriver",
                        type=str, help='chrome exe path')

    parser.add_argument('--output_folder_path', default="../data", type=str, help='Output folder path')
    args = parser.parse_args()
    main(args)

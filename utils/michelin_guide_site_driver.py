
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import numpy as np
from selenium.common.exceptions import NoSuchElementException

class MichelinGuideSiteDriver:
    """
    Michelin Guide Website Chrome Driver
    """
    def __init__(self, chrome_executable_path):
        self.chrome_executable_path = chrome_executable_path
        self.driver = None

    def open_driver(self):
        """
        Open Chrome Driver
        :return:
        """
        self.driver = webdriver.Chrome(executable_path=self.chrome_executable_path)

    def close_driver(self):
        """
        Close Chrome Driver
        :return:
        """
        self.driver.close()

    def get_michelin_restaurants_list(self, page, total_restaurant_number_in_page):
        """
        Get all restaurant list in Michelin Guide
        :param page: page number in Michelin Guide website
        :param total_restaurant_number_in_page: Total number of page number in website
        :return: Restaurant Names and URLs
        """
        links, names = [], []
        url = "https://guide.michelin.com/tr/en/restaurants/page/" + str(page)
        self.driver.get(url)
        for i in range(1, 1 + total_restaurant_number_in_page):
            if i == 1:  # sleep before first page
                time.sleep(3)
            xpath = f"/html/body/main/section[1]/div/div/div[2]/div[{i}]/div/a"

            restaurant = self.driver.find_element_by_xpath(xpath)
            link = restaurant.get_attribute('href')
            name = restaurant.get_attribute('aria-label')[5:]
            links.append(link)
            names.append(name)
        return np.array(names), np.array(links)

    def get_michelin_restaurant_data(self, url):
        """
        Get Metadata of the restaurant in Michelin Guide website
        :param url: URL of the restaurant
        :return: Restaurant Metadata
        """
        self.driver.get(url)

        restaurant_details = self.driver.find_element(By.CSS_SELECTOR,
                                                      "body > main > div.restaurant-details > div.container > div > div.col-xl-8.col-lg-7.restaurant-details__components > section.section.restaurant-details__main")
        restaurant_details_text = restaurant_details.get_attribute("innerText")
        restaurant_services = self.driver.find_element(By.CSS_SELECTOR,
                                                       "body > main > div.restaurant-details > div.container > div > div.col-xl-8.col-lg-7.restaurant-details__components > section:nth-child(2)")
        restaurant_services_text = restaurant_services.get_attribute("innerText")

        try:
            restaurant_open_hours = self.driver.find_element(By.CSS_SELECTOR,
                                                     "body > main > div.restaurant-details > div.container > div > div.col-xl-8.col-lg-7.restaurant-details__components > section:nth-child(3) > div.row > div:nth-child(1) > div > div.collapse__block-item.collapse-item")
            restaurant_open_hours_text = restaurant_open_hours.get_attribute("innerText")
        except:
            restaurant_open_hours_text = " "

        restaurant_contents = self.driver.find_element(By.CSS_SELECTOR, "#online-booking")
        restaurant_contents_text = restaurant_contents.get_attribute("innerText")

        return restaurant_contents_text, restaurant_details_text, restaurant_services_text, restaurant_open_hours_text

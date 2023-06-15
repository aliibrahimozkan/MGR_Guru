import sys
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class TripadvisorSiteDriver:

    def __init__(self) -> None:
        self.driver = None
        self.cookies_accepted = False

    def open_driver(self):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())

    def close_driver(self):
        self.driver.close()

    def __goto_tripadvisor_restaurant_link(self, restaurant_name: str, restaurant_location: str):
        """
        Searches a given restaurant in Tripadvisor to get its URL. Returns the URL.
        """
        self.driver.get("https://www.tripadvisor.com/")
        self.driver.implicitly_wait(10)

        # Accept cookies if necessary
        try:
            cookie_accept_element = self.driver.find_element_by_id("onetrust-accept-btn-handler")
            if cookie_accept_element.is_displayed():  # and self.cookies_accepted == False:
                cookie_accept_element.click()
                # self.cookies_accepted = True
        except:
            pass

        # Search restaurant in the search box, and get the link of the first result
        element_form = element_form = self.driver.find_element_by_xpath(
            ".//div[contains(@class, 'slvrn Z0 Wh EcFTp')]"). \
            find_element_by_xpath(".//form[contains(@class, 'hZNMq o') and @action='/Search']")
        element_input = element_form.find_element_by_xpath("input")
        element_input.click()
        element_input.send_keys(restaurant_name + " Restaurant " + restaurant_location)
        time.sleep(1)
        # element_results = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "typeahead_results")))
        top_result = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, ".//a[contains(@role, 'option') and contains(@href, 'Restaurant_Review')]")))
        # element_results = self.driver.find_element_by_xpath(".//div[contains(@id, 'typeahead_results') and contains(@class, 'ROqMU')]")
        # top_result = element_results.find_elements_by_xpath("a")[0]
        top_result.click()

    def __get_resturant_reviews(self, num_pages: int):
        """
        Reads review title, date, rating and text from Tripadvisor and returns corresponding lists.
        """
        review_titles = []
        review_users = []
        review_dates = []
        review_ratings = []
        review_texts = []

        # Accept cookies
        try:
            cookie_accept_element = self.driver.find_element_by_id("onetrust-accept-btn-handler")
            if cookie_accept_element.is_displayed():  # and self.cookies_accepted == False:
                cookie_accept_element.click()
                # self.cookies_accepted = True
        except:
            pass

        try:
            for i in range(0, num_pages):
                # expand the review
                container = self.driver.find_elements_by_xpath(".//div[@class='review-container']")
                for j in range(len(container)):
                    title = container[j].find_element_by_xpath(".//span[@class='noQuotes']").text
                    user = container[j].find_element_by_xpath(
                        ".//div[contains(@class,'info_text pointer_cursor')]").find_element_by_xpath(
                        "div").get_attribute("innerText")
                    date = container[j].find_element_by_xpath(".//span[contains(@class, 'ratingDate')]").get_attribute(
                        "title")
                    rating = container[j].find_element_by_xpath(
                        ".//span[contains(@class, 'ui_bubble_rating bubble_')]").get_attribute("class").split("_")[3]
                    review_text = container[j].find_element_by_xpath(".//p[@class='partial_entry']").text.replace("\n",
                                                                                                                  " ")

                    review_titles.append(title)
                    review_users.append(user)
                    review_dates.append(date)
                    review_ratings.append(rating)
                    review_texts.append(review_text)

                # change the page
                try:
                    next_page_element = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located(
                        (By.XPATH, ".//a[contains(@class,'nav next ui_button primary')]")))
                    if not "disabled" in next_page_element.get_attribute("class"):
                        next_page_element.click()
                        time.sleep(2)
                    else:
                        break
                except:
                    break
        except:
            return [review_titles, review_users, review_dates, review_ratings, review_texts]

        return [review_titles, review_users, review_dates, review_ratings, review_texts]


    def get_query_results(self, query: str, num_pages: int):
        """
        Forms an url with given query for TripAdvisor and returns top k results.
        """

        query_results = []
        self.driver.get("https://www.tripadvisor.com/")
        self.driver.implicitly_wait(10)

        # Accept cookies
        try:
            cookie_accept_element = self.driver.find_element_by_id("onetrust-accept-btn-handler")
            if cookie_accept_element.is_displayed():  # and self.cookies_accepted == False:
                cookie_accept_element.click()
        except:
            pass
        time.sleep(1)

        # Enter query in the search box
        element_form = self.driver.find_element_by_xpath(".//div[contains(@class, 'slvrn Z0 Wh EcFTp')]"). \
            find_element_by_xpath(".//form[contains(@class, 'hZNMq o') and @action='/Search']")
        element_input = element_form.find_element_by_xpath("input")
        element_input.click()
        element_input.send_keys("{}".format(query))
        element_input.send_keys(Keys.ENTER)
        time.sleep(3)

        # Accept cookies
        try:
            cookie_accept_element = self.driver.find_element_by_id("onetrust-accept-btn-handler")
            if cookie_accept_element.is_displayed():  # and self.cookies_accepted == False:
                cookie_accept_element.click()
        except:
            pass
        time.sleep(1)

        # Enter query in the search box
        element_form = self.driver.find_element_by_xpath(
            ".//div[contains(@class, 'slvrn Z0 Wh UfhjQ')]").find_element_by_xpath(
            ".//form[contains(@class, 'hZNMq o') and @action='/Search']")
        element_input = element_form.find_element_by_xpath("input")
        element_input.click()
        element_input.clear()
        element_input.send_keys("michelin star restaurants {}".format(query))
        element_input.send_keys(Keys.ENTER)
        time.sleep(3)

        # Click "Show More" button
        try:
            show_more_btn_element = self.driver.find_element_by_xpath(".//span[@class='ui_link show-text']")
            if show_more_btn_element.is_displayed():
                show_more_btn_element.click()
        except:
            pass

        self.driver.implicitly_wait(0)
        # For a pre-determined number of pages, get titles and ratings of the restaurants
        for i in range(num_pages):
            # Get results and ratings
            try:
                all_results_div_element = self.driver.find_element_by_xpath(
                    ".//div[@class='ui_columns is-multiline is-mobile']")
            except:
                break
            results = all_results_div_element.find_elements_by_xpath(
                ".//div[@class='prw_rup prw_search_search_result_poi']")

            for result in results:
                michelin_title = False
                try:
                    michelin_title_element = WebDriverWait(result, 0.05).until(
                        EC.presence_of_element_located((By.XPATH, ".//div[@class='michelin-title']")))
                    michelin_title = True
                except:
                    pass
                if michelin_title:
                    title = result.find_element_by_xpath(".//div[@class='result-title']").find_element_by_xpath(
                        "span").get_attribute("innerText")
                    rating = float(
                        result.find_element_by_xpath(".//div[@class='rating-review-count']").find_element_by_xpath(
                            ".//span[contains(@class, 'ui_bubble_rating')]").get_attribute("alt").split(" ")[0])
                    query_results.append((title, rating))

            # Change the page
            try:
                next_page_element = WebDriverWait(self.driver, 1).until(
                    EC.presence_of_element_located((By.XPATH, ".//a[contains(@class,'ui_button nav next primary')]")))
                if not "disabled" in next_page_element.get_attribute("class"):
                    next_page_element.click()
                    time.sleep(2)
                else:
                    break
            except:
                break

            time.sleep(2)

        self.driver.implicitly_wait(5)

        return query_results

    def get_reviews_ratings(self, restaurant_name: str, restaurant_location: str, num_pages: int):
        review_titles = []
        review_users = []
        review_dates = []
        review_ratings = []
        review_texts = []

        try:
            self.__goto_tripadvisor_restaurant_link(restaurant_name=restaurant_name,
                                                    restaurant_location=restaurant_location)
            review_titles, review_users, review_dates, review_ratings, review_texts = self.__get_resturant_reviews(
                num_pages=num_pages)
        except:
            return review_titles, review_users, review_dates, review_ratings, review_texts
        return review_titles, review_users, review_dates, review_ratings, review_texts
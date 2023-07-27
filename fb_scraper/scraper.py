import logging

from selenium.common.exceptions import NoSuchElementException
from fb_scraper.utils.logger_config import setup_logger
from enum import IntEnum
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait, TimeoutException
from selenium.webdriver.support import expected_conditions as EC


class Sort(IntEnum):
    TOP_POSTS = 0
    RECENT_ACTIVITY = 1
    CHRONOLOGICAL = 2
    TOP_LISTINGS = 3
    RECENT_LISTING_ACTIVITY = 4
    NEARBY_LISTINGS = 5
    CHRONOLOGICAL_LISTINGS = 6


class FacebookScraper:
    def __init__(self, headless=True):
        self.fb_url = r'https://www.facebook.com/'
        self.logger = setup_logger(__name__)
        self.driver = None

        options = Options()
        if headless is True:
            options.add_argument('--headless')

        self.to_fb(options)

    def to_fb(self, options):
        self.driver = webdriver.Chrome(service=Service('./chromedriver'), options=options)
        self.driver.get(self.fb_url)

        wait = WebDriverWait(self.driver, 5)
        try:
            wait.until(EC.presence_of_element_located((By.NAME, 'email')))
        except TimeoutException as e:
            self.logger.error('FAILED TO LOAD LOGIN PAGE')
            raise e
        else:
            self.logger.info('Loaded login page')

    def login(self, acc, passwd):
        acc_box = self.driver.find_element(By.NAME, 'email')
        passwd_box = self.driver.find_element(By.NAME, 'pass')
        acc_box.send_keys(acc)
        passwd_box.send_keys(passwd)

        login_button = self.driver.find_element(By.NAME, 'login')
        login_button.click()

        wait = WebDriverWait(self.driver, 30)
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label=Facebook]')))
        except TimeoutException as e:
            self.logger.error('FAILED TO LOAD HOMEPAGE')
            raise e
        else:
            self.logger.info('Loaded homepage')

    def to_group(self, group_id, sort=Sort.TOP_POSTS):
        sorting_setting = ['TOP_POSTS', 'RECENT_ACTIVITY', 'CHRONOLOGICAL',
                           'TOP_LISTINGS', 'RECENT_LISTING_ACTIVITY',
                           'NEARBY_LISTINGS', 'CHRONOLOGICAL_LISTINGS']
        group_url = self.fb_url + f"groups/{group_id}?sorting_setting={sorting_setting[sort]}"
        self.driver.get(group_url)

        wait = WebDriverWait(self.driver, 60)
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@data-ad-preview="message"]')))
        except TimeoutException as e:
            self.logger.error('FAILED TO LOAD GROUP PAGE')
            raise e
        else:
            self.logger.info('Loaded group page')

    def refresh(self):
        logging.info('Refreshing page...\n')
        self.driver.refresh()

    def fetch_post(self):
        latest_post = self.driver.find_element(By.XPATH, '//*[@data-ad-preview="message"]')
        post_content = self.get_post_content(latest_post)
        listing_text = self.get_listing_text(latest_post)
        post_url = self.get_post_url(latest_post)
        post_id = post_url.split('/')[-1].split('?')[0]
        return {
            'id': post_id,
            'url': post_url,
            'content': post_content,
            'listing_text': listing_text,
        }

    @staticmethod
    def get_listing_text(post):
        listing_text = None
        try:
            listing_text = post.find_element(By.XPATH,
                                             '../../div[2]/div[1]/div/a[2]/div[1]/div/div[2]/span/span/div')
        except NoSuchElementException:
            try:
                listing_text = post.find_element(By.XPATH,
                                                 '../../div[2]/div[1]/div/a/div[1]/div/div[2]/span/span/div')
            except NoSuchElementException:
                logging.error("FAILED TO FETCH LISTING TEXT")
                return ''

        return listing_text

    @staticmethod
    def get_post_content(post):
        post_content = post.find_elements(By.XPATH, './div/div/span/div/div')
        try:
            more = post_content[-1].find_element(By.XPATH, './div')
            more.send_keys(Keys.RETURN)
            logging.info('Expanding post')
        except NoSuchElementException:
            logging.info("No need to expand post")

        try:
            post_content = post.find_elements(By.XPATH, './div/div/span/div/div')
            content = '\n'.join(list(map(lambda x: x.text, post_content)))
        except NoSuchElementException:
            logging.error('FAILED TO FETCH POST')
        else:
            return content

    def get_post_url(self, post):
        try:
            ac = ActionChains(self.driver)
            timestamp = post.find_element(By.XPATH,
                                          '../../../div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a')
            ac.move_to_element(timestamp).perform()
            timestamp = post.find_element(By.XPATH,
                                          '../../../div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a')
        except NoSuchElementException:
            try:
                ac = ActionChains(self.driver)
                timestamp = post.find_element(By.XPATH,
                                              '../../../div[2]/div/div[2]/div/div[2]/span/span/span[4]/span/a')
                ac.move_to_element(timestamp).perform()
                timestamp = post.find_element(By.XPATH,
                                              '../../../div[2]/div/div[2]/div/div[2]/span/span/span[4]/span/a')
            except NoSuchElementException as e:
                logging.error('FAILED TO FETCH POST URL')
                raise e

        post_url = timestamp.get_attribute('href').split('/?')[0]
        return post_url


if __name__ == '__main__':
    scraper = FacebookScraper(headless=True)
    scraper.login('***REMOVED***', '***REMOVED***')
    scraper.to_group(***REMOVED***, Sort.CHRONOLOGICAL_LISTINGS)
    print(scraper.fetch_post())

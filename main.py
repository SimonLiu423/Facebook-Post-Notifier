import os.path

from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pickle
import logging
import yaml
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import LineBotApiError
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from utils.crypto.decrypt import decrypt
import sys

logging.basicConfig(level=logging.INFO, filename='log.txt', filemode='w',
                    format='[%(asctime)s %(levelname)-8s] %(message)s',
                    datefmt='%Y%m%d %H:%M:%S',
                    encoding='utf-8',
                    )


def decrypt_yaml(path):
    decrypted_data = decrypt(path)
    try:
        yaml_data = yaml.safe_load(decrypted_data)
        return yaml_data
    except yaml.reader.Reader:
        logging.error("YAML failed to load, could be wrong password")
        print("Wrong password.")
        sys.exit()


# FB & Line bot credentials
cred = decrypt_yaml('credentials.yaml.encrypted')
access_token = cred['line_bot']['channel_access_token']
fb_acc = cred['fb_cred']['account']
fb_pass = cred['fb_cred']['password']
group_id = cred['receivers']['group_id']

# Load configs
with open('config.yaml') as f:
    config = yaml.safe_load(f)
url = config['url']

line_bot_api = LineBotApi(access_token)
prev_post_path = 'prev_post.pickle'

keywords = ['便當', '餐盒', '三明治', '飯糰', '剩下', '多的', '發不完']


def main():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    # Instantiate a new WebDriver object and navigate to Facebook:
    driver = webdriver.Chrome('./chromedriver', chrome_options=chrome_options)  # Replace with the appropriate driver
    driver.get('https://www.facebook.com/')
    driver.implicitly_wait(5)

    # Login to Facebook
    acc_input = driver.find_element(By.NAME, 'email')
    passwd_input = driver.find_element(By.NAME, 'pass')
    acc_input.send_keys(fb_acc)
    passwd_input.send_keys(fb_pass)
    login_button = driver.find_element(By.NAME, 'login')
    login_button.click()

    # Wait for page to load
    time.sleep(1)

    # Navigate to group's page
    global url
    url = url + '?sorting_setting=CHRONOLOGICAL_LISTINGS'
    driver.get(url)

    if not os.path.exists(prev_post_path):
        with open(prev_post_path, 'wb') as f:
            pickle.dump('', f)

    with open(prev_post_path, 'rb') as f:
        prev_post_context = pickle.load(f)

    while True:
        try:
            newest_post = driver.find_element(By.XPATH, '//*[@data-ad-preview="message"]')
            post_context = newest_post.find_elements(By.XPATH, './div/div/span/div/div')
        except:
            logging.error('ERROR FETCHING POST')

        try:
            more = post_context[-1].find_element(By.XPATH, './div')
            more.send_keys(Keys.RETURN)
            logging.info('Expanding post')
        except:
            logging.info("No need to expand post")

        try:
            post_context = newest_post.find_elements(By.XPATH, './div/div/span/div/div')
            context = '\n'.join(list(map(lambda x: x.text, post_context)))
            logging.info('Newest context:\n' + context)
        except:
            logging.error('ERROR FETCHING POST')

        if prev_post_context != context:
            logging.info("IT'S A NEW POST!")
            prev_post_context = context
            with open(prev_post_path, 'wb') as f:
                pickle.dump(context, f)

            if any(kw in context for kw in keywords):
                push_message = '你各位蹭飯啦！！！\n\n' + context
                try:
                    logging.info('Sending push message...')
                    line_bot_api.push_message(group_id, TextSendMessage(text=push_message))
                except LineBotApiError as e:
                    logging.error(e)

            # subprocess.call(["./line_push.sh"])

        logging.info("Refreshing page...")
        driver.refresh()
        time.sleep(20)


if __name__ == '__main__':
    main()

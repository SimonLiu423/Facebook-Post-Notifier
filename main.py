import os.path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pickle
import logging
import yaml
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import LineBotApiError
from selenium.webdriver.chrome.options import Options
import subprocess

logging.basicConfig(level=logging.INFO, filename='log.txt', filemode='w',
                    format='[%(asctime)s %(levelname)-8s] %(message)s',
                    datefmt='%Y%m%d %H:%M:%S',
                    )

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

account = config['credentials']['account']
password = config['credentials']['password']
channel_access_token = config['LineBot']['channel_access_token']
user_id = config['Line']['user_id']

line_bot_api = LineBotApi(channel_access_token)
# handler = WebhookHandler(config['LineBot']['channel_secret'])
prev_post_path = 'prev_post.pickle'

# os.environ["CHANNEL_ACCESS_TOKEN"] = channel_access_token
# os.environ['USER_ID'] = user_id

app = Flask(__name__)

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
    acc_input.send_keys(account)
    passwd_input.send_keys(password)
    login_button = driver.find_element(By.NAME, 'login')
    login_button.click()

    # Wait for page to load
    time.sleep(1)

    # Navigate to group's page
    group_name = 'NCKUhouse'
    group_url = f'https://www.facebook.com/groups/{group_name}?sorting_setting=CHRONOLOGICAL_LISTINGS'
    driver.get(group_url)

    if not os.path.exists(prev_post_path):
        with open(prev_post_path, 'wb') as f:
            pickle.dump('', f)

    with open(prev_post_path, 'rb') as f:
        prev_post_context = pickle.load(f)

    while True:
        # Get the number of posts
        posts = driver.find_elements(By.XPATH, '//div[@class="x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z"]')
        current_post_count = len(posts)

        newest_post = driver.find_elements(By.XPATH, '//*[@data-ad-preview="message"]/div/div/span/div/div')
        context = '\n'.join(list(map(lambda x: x.text, newest_post)))
        logging.info('Newest context:\n' + context)

        if prev_post_context != context:
            logging.info("IT'S A NEW POST!")
            prev_post_context = context
            with open(prev_post_path, 'wb') as f:
                pickle.dump(context, f)

            # os.environ["LINE_PUSH_CONTEXT"] = str(context.encode('unicode_escape'))
            # TODO: Push preview context to chat
            push_message = '成大租屋 嗷ㄨ嗷ㄨ 有新貼文！\n{}\n\n'.format(group_url) + context
            try:
                logging.info('Sending push message...')
                line_bot_api.push_message(user_id, TextSendMessage(text=push_message))
            except LineBotApiError as e:
                logging.error(e)

            # subprocess.call(["./line_push.sh"])

        logging.info("Refreshing page...")
        driver.refresh()


if __name__ == '__main__':
    main()

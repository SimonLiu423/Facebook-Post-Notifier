import argparse
import os.path
import time
import pickle
import logging
import yaml
import sys
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
from fb_scraper.utils.crypto.decrypt import decrypt
from fb_scraper.utils.logger_config import setup_logger
from fb_scraper.scraper import FacebookScraper, Sort
from selenium.common.exceptions import TimeoutException

logger = setup_logger(__name__)


def decrypt_yaml(path):
    decrypted_data = decrypt(path)
    try:
        yaml_data = yaml.safe_load(decrypted_data)
        return yaml_data
    except yaml.reader.ReaderError:
        logger.error("YAML failed to load, may be due to incorrect password or invalid YAML format.")
        sys.exit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('enc_file', help='Encrypted config file')
    parser.add_argument('type', help='Type of post you wish to scrape, "listing" or "post"')
    parser.add_argument('-H', '--headless', action='store_true')
    args = parser.parse_args()

    sort_type = None
    headless = args.headless

    if args.type == 'listing':
        sort_type = Sort.CHRONOLOGICAL_LISTINGS
    elif args.type == 'post':
        sort_type = Sort.CHRONOLOGICAL
    else:
        print('Expected --type "listing" or "post"')
        sys.exit(1)

    enc_file = args.enc_file
    if not os.path.exists(enc_file):
        print('File not found.')
        sys.exit(1)

    config = decrypt_yaml(enc_file)
    interval = 10

    scraper = FacebookScraper(headless=headless)
    scraper.login(config['fb_cred']['account'], config['fb_cred']['password'])

    line_bot_api = LineBotApi(config['line_bot']['channel_access_token'])
    keywords = config['keywords']
    prev_post_id = None
    while True:
        try:
            scraper.to_group(config['group_id'], Sort.CHRONOLOGICAL_LISTINGS)
        except TimeoutException:
            logger.info(f'Waiting {interval} secs...')
            time.sleep(interval)
            logger.info('Refreshing page...')
            continue

        latest_post = scraper.fetch_post()
        logger.info('Latest post:')
        logger.info(latest_post)

        if prev_post_id is not None and prev_post_id != latest_post['id']:
            logger.info('NEW POST!')
            if any(kw in latest_post['content'] for kw in keywords) or any(
                    kw in latest_post['listing_text'] for kw in keywords):
                logger.info('Keyword found!')
                push_message = config['message'].format(url=latest_post['url'], content=latest_post['content'],
                                                        listing_text=latest_post['listing_text'])
                for user in config['receivers']:
                    try:
                        logger.info('Sending message to {}...'.format(user))
                        line_bot_api.push_message(config['receivers'][user], TextSendMessage(text=push_message))
                    except LineBotApiError as e:
                        logger.error(e)
                        raise e

        prev_post_id = latest_post['id']
        logger.info(f'Waiting {interval} secs...')
        time.sleep(interval)
        logger.info('Refreshing page...')

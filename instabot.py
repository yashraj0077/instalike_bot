import sys
from utils import *
from insta_logging.insta_logging import insta_logger
from scraping_models import CrawlFollowing
from public_api_models import LikingBot

__author__ = 'sehlat57'


def main():
    bot = None
    try:
        # Parsing args from command-line
        args = parse_credentials()
        login = args.login
        password = args.password
        posts_to_check = args.number_of_posts
        ignore_limit = args.ignore_limit
        insta_logger.info('--------------START---------------')
        draw_line_separator()
        draw_logo()
        draw_line_separator()
        print('instabot is working:')
        draw_worker_text('populating ignore list')
        ignore_list = load_ignore_list()
        draw_line_separator()
        draw_worker_text('getting list of followings')
        print('#This could take a while, be patient#')

        # Selenium part:
        # using PhantomJS headless web browser to login and
        # gather links of the accounts that user follows
        web_driver = CrawlFollowing(user_login=login, user_password=password)
        web_driver.login()
        web_driver.crawl_folowing_links()
        followings_list = web_driver.followings_list
        web_driver.close()

        # Public api part using requests library:
        draw_line_separator()
        draw_worker_text('Liking posts')
        bot = LikingBot(user_login=login, user_password=password,
                        ignore_list=ignore_list, followings=followings_list,
                        posts_to_check=posts_to_check,
                        ignore_limit=ignore_limit)
        # Login with 'requests' to use instagram public api
        bot.public_api.login()
        bot.populate_post_list()  # Populating users media data
        # Excluding posts that have already been liked
        bot.excluding_liked_posts()
        bot.liking_all_posts()  # Liking all remaining posts
        draw_worker_text('Work is done, bot is tired and shutting down.')
        draw_worker_text('For more info refer to today log file')
        insta_logger.info('End of the program. Shutting down')
        insta_logger.info(
            '--------------STOP---------------')
        bot.public_api.logout()
        sys.exit()

    except KeyboardInterrupt:
        print('\nBot was interrupted by user. Shutting down')
        insta_logger.info('Program is interrupted by user. Shutting down')
        if bot and bot.public_api.logged_in:
            bot.public_api.logout()
        insta_logger.info(
            '--------------STOP---------------')
        sys.exit()


if __name__ == '__main__':
    main()

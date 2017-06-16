import os
import sys
from time import time
from datetime import date
import argparse
import textwrap
import json
import io

from insta_logging.insta_logging import insta_logger

__author__ = 'sehlat57'


def load_ignore_list():
    """
    Get names of users from file to be excluded from liking list
    :return: list of users to be ignored, empty list if file structure is
    modified or not found
    """
    dir_name = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(os.path.join(dir_name, 'ignore_list.txt')):
        with open('ignore_list.txt', 'r') as ignore_list_file:
            full_text = ignore_list_file.read()
            if full_text.find('Ignore list:') != -1:
                start_index = full_text.index('Ignore list:') + len(
                    'Ignore list:')
                list_raw = full_text[start_index:].split(',')
                insta_logger.info('Ignore list extracted')
                print('Ignore list extracted')
                return [account.strip() for account in list_raw]
            print('"Ignore list.txt" was edited incorrectly. '
                  'Can\'t create ignore list.'
                  ' Please see description.')
            insta_logger.error('Ignore list file incorrectly edited')
            return []
    print('No ignore list found')
    insta_logger.error('No ignore list found')
    return []


def parse_credentials():
    """
    Parse arguments:
    required:
    -login - instagram user name
    -password - password for the account
    optional:
    -number_of_posts - number of posts to like (default: 12)
    -ignore_limit - ignore 1000 likes by bot per day limit (default: False)

    :return: parsed arguments from command line
    """
    parser = argparse.ArgumentParser(
        prog='InstaLikeBot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
        --------------------------------------------
        Instagram bot for liking posts of followings.
        You need to enter your Instagram credentials
        and number of post to check for your likes
        (default number is 12).
        --------------------------------------------
        Be warned: there is possibility to be banned
        if bot likes to many posts (1000+ per day).
        If you want to ignore '1000 likes per day limit'
        add --ignore_limit argument
        --------------------------------------------
        Example:
        python3 instabot.py -l ACCOUNT_NAME -p PASSWORD -n 12 -limit False
        ____________________________________________
    
        '''))
    parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    required.add_argument('-l', '--login',
                          required=True,
                          help='\nInstagram account name')
    required.add_argument('-p', '--password',
                          required=True,
                          help='\nInstagram password')
    required.add_argument('-n', '--number_of_posts',
                          type=int,
                          default=12,
                          help='\nNumber of posts to check for user likes, '
                               'default value is 12')
    required.add_argument('--ignore_limit',
                          action='store_true',
                          default=False,
                          help='\nAdd --ignore_limit if you want to '
                               'ignore limit of 1000 likes per day')
    args = parser.parse_args()
    if args.number_of_posts <= 0:
        parser.error('Number of posts must be greater than 0')
    return args


def draw_line_separator():
    """
    Draw line in stdout
    :return:
    """
    print(''.center(50, '-'))


def draw_worker_text(text):
    """
    Formatting text
    :param text: text to format
    :return:
    """
    print('@{}@'.format(text).center(50))


def progress_bar(completion, total, start_time, width=20):
    """
    Print progress bar in stdout
    :param completion: extracted/liked posts to the moment
    :param total: total posts
    :param start_time: time stamp before first appear of progress bar in stdout
    :param width: width of progress bar
    :return:
    """
    progress = int(completion / total * 100)
    completion = completion
    total = total
    seconds_passed = time() - start_time
    time_stamp = '{:02.0f}:{:02.0f}:{:02.0f}'.format(
        seconds_passed // 3600, seconds_passed % 3600 // 60,
        seconds_passed % 60)
    bar = '\x1b[1;30;46m \x1b[0m' * int(
        width * completion / total) + ' ' * int(
        width - (width * completion / total))
    show = ('\r{}%|{}|{}/{}|time passed: {}'.format(
        progress if progress < 100 else 100, bar, completion, total,
        time_stamp))
    sys.stdout.write(show)
    sys.stdout.flush()
    if completion >= total:
        sys.stdout.write('\n')


def write_today_likes(total_likes):
    """
    Write number of today likes made by bot to file in json:
     {"date": "total likes"}
    :param total_likes: number of likes
    :return:
    """
    dir_name = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(dir_name, 'likes_count.json'),
              'w') as likes_file:
        try:
            likes = json.load(likes_file)
        except io.UnsupportedOperation:
            likes = dict()
        likes[str(date.today())] = total_likes
        json.dump(likes, likes_file)
        insta_logger.info('Likes made by bot is writen to file, '
                          'total posts liked today: {}'.format(total_likes))


def read_today_likes():
    """
    Read number of likes made by bot from json file
    :return: number of likes made by bot today, 0 if today date not found
    """
    dir_name = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(dir_name, 'likes_count.json')
    if os.path.exists(file_path):
        with open(file_path) as likes_file:
            try:
                likes = json.load(likes_file)
                likes_today = likes.get(str(date.today()))
                if likes_today:
                    return likes_today
                return 0
            except io.UnsupportedOperation:
                return 0
    return 0


def draw_logo():
    print("""

     _              _          _             _   
    (_) _ __   ___ | |_  __ _ | |__    ___  | |_ 
    | || '_ \ / __|| __|/ _` || '_ \  / _ \ | __|
    | || | | |\__ \| |_| (_| || |_) || (_) || |_ 
    |_||_| |_||___/ \__|\__,_||_.__/  \___/  \__|


           """)
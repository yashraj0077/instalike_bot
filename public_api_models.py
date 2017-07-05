import time
from time import time as current_time
import sys
import requests
import random
from urllib.parse import urljoin, urlparse

from insta_logging.insta_logging import insta_logger
from utils import progress_bar, check_today_likes, write_likes

__author__ = 'sehlat57'


class InstApi(object):
    main_url = 'https://www.instagram.com/'
    login_url = 'https://www.instagram.com/accounts/login/ajax'
    logout_url = 'https://www.instagram.com/accounts/logout/'
    user_agent = '"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 ' \
                 '(KHTML, like Gecko) Chrome/15.0.87"'
    headers = {
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Content-Length': '0',
        'Host': 'www.instagram.com',
        'Origin': 'https://www.instagram.com',
        'Referer': 'https://www.instagram.com/',
        'X-Instagram-AJAX': '1',
        'X-Requested-With': 'XMLHttpRequest'
    }

    def __init__(self, user_login, user_password, ignore_list,
                 posts_to_check):
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.session.headers.update({'User-Agent': self.user_agent})
        self.user_login = user_login
        self.user_password = user_password
        self.ignore_list = ignore_list
        self.posts_to_check = posts_to_check
        self.pagination = posts_to_check // 12 if posts_to_check >= 12 else 12
        self.logged_in = False

    def login(self, attempts=3):
        """
        Login to instagram account with 'requests'
        :param attempts: number of attempts to login, default is 3,
        shutting down if failed to login
        :return: 1 if login successful
        """
        print('-Trying to login to account to use public api')
        for attempt in range(attempts):
            try:
                print('-Login attempt {} of {}'.format(
                    attempt + 1, attempts))
                self.session.get(self.login_url)
                csrf_token = self.session.cookies['csrftoken']
                self.session.headers.update({'X-CSRFToken': csrf_token})
                time.sleep(3)
                login_to_acc = self.session.post(
                    self.login_url,
                    data={'username': self.user_login,
                          'password': self.user_password},
                    allow_redirects=True)
                time.sleep(3)
                if login_to_acc.status_code == 200:
                    main_page = self.session.get(self.main_url)
                    if main_page.text.find(self.user_login) != -1:
                        print('--Successful login')
                        insta_logger.info('Requests: Successful login')
                        self.session.headers.update({
                            'X-CSRFToken': login_to_acc.cookies['csrftoken']})
                        self.logged_in = True
                        return 1
                    print('--Login failed, wrong credentials')
                    insta_logger.error('Requests: Login failed (status code: '
                                       '{}), credentials: login: {} password:'
                                       ' {}, attempt: {}'.format(
                        login_to_acc.status_code, self.user_login,
                        self.user_password, attempt))
                else:
                    print('--Login failed, status code: {}'.format(
                        login_to_acc.status_code))
                    insta_logger.error('Requests: login failed (status code: '
                                       '{}), credentials: login: {} password: '
                                       '{}, attempt: {}'.format(
                        login_to_acc.status_code, self.user_login,
                        self.user_password, attempt))
            except Exception as e:
                insta_logger.error(
                    'Requests: login error, Exception: {}, attempt {}'.format(
                        e, attempt + 1))
                print('--Failed. Exception raised.')
        insta_logger.critical('Requests: unable to login.'
                              'Shutting down')
        insta_logger.info('--------------STOP---------------')
        print('Unable to login. Refer to log file. '
              'Shutting down')
        sys.exit()

    def logout(self):
        """
        Logout from account with 'requests'
        :return:
        """
        try:
            logout_page = self.session.get(self.logout_url)
            time.sleep(3)
            if logout_page.status_code == 200:
                insta_logger.info('Successful logout')
            else:
                insta_logger.error('Failed logout, status code: {}'.format(
                    logout_page.status_code))
        except Exception as e:
            insta_logger.error('Failed logout, exception: {}'.format(e))

    def get_recent_media_feed(self, url):
        """
        Function gather data about user recent posts: posts ids and posts codes
        To get json response with user media data query param '?__a=1' must be
        added to end of url. Response return max value of 12 posts, to get more
        posts query param &max_id='page_num' must be added.
        :param url: instagram user url
        :return: dictionary with user as key and set of tuples with posts media
        code and media id as value
        """
        main_url = urljoin(url, '?__a=1')
        step = 0
        end_cursor = None
        username = urlparse(url)[2].strip('/')
        media_data = {username: set()}
        try:
            while step != self.pagination + 1:
                if end_cursor:
                    query = '&max_id={}'.format(end_cursor)
                    feed_url = '{}{}'.format(main_url, query)
                else:
                    feed_url = main_url
                feed_page_raw = self.session.get(feed_url)
                json_data = feed_page_raw.json()
                if username in self.ignore_list:
                    insta_logger.info(
                        'User {} is in ignore list'.format(username))
                    return
                try:
                    feed_data = json_data['user']['media']['nodes']
                    if feed_data:
                        for media in feed_data:
                            media_data[username].add((media['code'],
                                                      media['id']))
                            if len(media_data[
                                       username]) >= self.posts_to_check:
                                insta_logger.info(
                                    'User {} media data extracted,'
                                    ' total media {}'.format(
                                        username, len(media_data[username])
                                    ))
                                return media_data
                        step += 1
                        if json_data['user'][
                            'media']['page_info']['has_next_page']:
                            end_cursor = json_data[
                                'user']['media']['page_info']['end_cursor']
                            time.sleep(1 * random.random())
                        else:
                            break
                    else:
                        insta_logger.info(
                            'User {} has no media data, ignored'.format(
                                username))
                        return
                except KeyError:
                    insta_logger.error(
                        'Key error while getting media feed, user {}'.format(
                            username))
                    return
            insta_logger.info(
                'User {} media data extracted, total media {}'.format(
                    username, len(media_data[username])
                ))
            return media_data
        except Exception as e:
            insta_logger.error('Exception raised while getting feed data,'
                               'Exeption: {}'.format(e))

    def like_media(self, media_id, media_code, username):
        """
        Function is used to like user post using instagram public api
        (AJAX requests)
        :param media_id: id of the post
        :param media_code: code of the post
        :param username: username (of the followings)
        :return:
        """
        url_like = 'https://www.instagram.com/web/likes/{}/like/'.format(
            media_id)
        try:
            post_like = self.session.post(url_like)
            if post_like.status_code == 200:
                insta_logger.info('User {} post code #{} was liked'.format(
                    username, media_code))
                return 1
            else:
                insta_logger.error('Failed to like user {} post code #{},'
                                   'status code: {}'.format(username,
                                                            media_code,
                                                            post_like.status_code))
        except Exception as e:
            insta_logger.error(
                'Exception raised while liking user {} post code #{}'
                'Exception: {}'.format(username, media_code, e))

    def check_like(self, media_code, username):
        """
        Function check if post have been already liked using instagram
        public api (AJAX requests)
        :param media_code: code of the post
        :param username: username (of the followings)
        :return: 1 if post has benn already liked
        """
        media_url = 'https://www.instagram.com/p/{}/?__a=1'.format(media_code)
        try:
            media_data = self.session.get(media_url).json()
            try:
                liked = media_data[
                    'graphql']['shortcode_media']['viewer_has_liked']
                if liked:
                    return 1
            except KeyError:
                insta_logger.error(
                    'Key error while checking if media is liked by user {},'
                    ' media code{}'.format(
                        username, media_code))

        except Exception as e:
            insta_logger.error('Exception raised while checking'
                               'if media is liked by user {}, media code: {}'
                               'Exception: {}'.format(username, media_code, e))


class LikingBot(object):
    def __init__(self, user_login, user_password, ignore_list, followings,
                 posts_to_check=12, ignore_limit=False):
        self.public_api = InstApi(user_login=user_login,
                                  user_password=user_password,
                                  ignore_list=ignore_list,
                                  posts_to_check=posts_to_check
                                  )
        self.ignore_limit = ignore_limit
        self.followings = followings
        self.posts_to_like = dict()
        self.timestamp = time.time()
        self.total_likes = check_today_likes(self.timestamp)
        self.like_errors = 0
        self.like_error_limit = 3
        self.like_error_posts = dict()

    @staticmethod
    def calc_num_of_posts(posts):
        """
        Function calculate number of posts of all users
        :param posts: dictionary with users as keys and posts data as values
        :return: number of posts of all users
        """
        return sum([len(post) for post in posts.values() if post])

    def check_likes_limit(self, write_timestamp=True):
        """
        Checks if likes made by bot not exceeds limit (1000 likes)
        If likes made today equal limit - exit program.
        :return:
        """
        if not self.ignore_limit:
            if self.total_likes >= 1000:
                insta_logger.critical('Bot liked 1000 posts in recent '
                                      '24 hours,'
                                      'stopping bot to avoid ban')
                if write_timestamp:
                    write_likes(self.total_likes)
                insta_logger.info(
                    '--------------STOP---------------')
                print('Bot liked 1000 posts in recent 24 hours, '
                      'stopping bot to avoid ban')
                if self.public_api.logged_in:
                    self.public_api.logout()
                sys.exit()

    def populate_post_list(self):
        """
        Populate posts to like from list of followings using 'InstApi'
        'get_recent_media_feed' method
        :return:
        """
        print('-Extracting users media')
        start_time = current_time()
        total_links = len(self.followings)
        completion = 0
        for user_url in self.followings:
            media_data = self.public_api.get_recent_media_feed(user_url)
            if media_data:
                self.posts_to_like.update(media_data)
            completion += 1
            progress_bar(completion=completion, total=total_links,
                         start_time=start_time)
        if not self.posts_to_like:
            insta_logger.critical('No posts media extracted, shutting down')
            insta_logger.info(
                '--------------STOP---------------')
            print('No posts to like. Shutting down.')
            self.public_api.logout()
            sys.exit()

    def excluding_liked_posts(self):
        """
        Exclude data from the set of posts that have already been liked using
        'InstApi' 'check_like' method
        :return:
        """
        print('-Excluding posts that have already been liked')
        start_time = current_time()
        total_posts = self.calc_num_of_posts(self.posts_to_like)
        completion = 0
        for user, posts in self.posts_to_like.items():
            liked_posts = set()
            for post in posts:
                liked = self.public_api.check_like(media_code=post[0],
                                                   username=user)
                if liked:
                    liked_posts.add(post)
                completion += 1
                progress_bar(completion=completion, total=total_posts,
                             start_time=start_time)
            insta_logger.info('User {} total liked posts excluded: {}'.format(
                user, len(liked_posts)))
            posts.difference_update(liked_posts)

    def liking_all_posts(self):
        """
        Liking followings posts using 'InstApi' 'like_media' method
        :return:
        """
        total_posts = self.calc_num_of_posts(self.posts_to_like)
        if total_posts == 0:
            insta_logger.critical('No posts to like, shutting down')
            insta_logger.info(
                '--------------STOP---------------')
            print('No posts to like. Shutting down.')
            self.public_api.logout()
            sys.exit()
        print('-Liking followings posts')
        print('--Total posts to like: {}'.format(total_posts))
        start_time = current_time()
        completion = 0
        liked = 0
        for user, posts in self.posts_to_like.items():
            for post in posts:
                self.check_likes_limit()
                like_post = self.public_api.like_media(media_id=post[1],
                                                       media_code=post[0],
                                                       username=user)
                if like_post:
                    liked += 1
                    self.total_likes += 1
                else:
                    self.like_errors += 1
                    self.like_error_posts.setdefault(user, set()).add(post)
                    if self.like_errors == self.like_error_limit:
                        self.like_errors = 0
                        print('\n')
                        print('\n oops, something is wrong,'
                              'login again after 5 minutes\n'
                              'please wait')
                        self.public_api.logout()
                        time.sleep(60 * 5)
                        insta_logger.info('Relogin attempt')
                        self.public_api.login()
                        print('Resume liking')
                completion += 1
                progress_bar(completion=completion, total=total_posts,
                             start_time=start_time)
                time.sleep(1 * random.random())
        session_failed = self.calc_num_of_posts(self.like_error_posts)
        print('--Successfully liked in session: {}'.format(liked))
        insta_logger.info('Successfully liked in session: {}'.format(
            liked))
        print('--Failed to like in session: {}'.format(session_failed))
        insta_logger.info('Failed to like in '
                          'session: {}'.format(session_failed))
        write_likes(self.total_likes)

    def reliking_failed_posts(self):
        """
        Liking posts, that 'bot' failed to like during first session
        :return:
        """
        total_posts_to_relike = self.calc_num_of_posts(self.like_error_posts)
        if total_posts_to_relike != 0:
            print('-Logout and sleep for 2 minutes before "reliking" session')
            insta_logger.info('Logout and sleep for 2 minutes before'
                              ' "reliking" session')
            self.public_api.logout()
            time.sleep(2 * 60)
            print('-Trying to relogin to relike "failed posts"')
            insta_logger.info('Relogin to like "failed posts"')
            self.public_api.login()
            start_time = current_time()
            completion = 0
            liked = 0
            failed_to_like = 0
            for user, posts in self.like_error_posts.items():
                for post in posts:
                    self.check_likes_limit()
                    like_post = self.public_api.like_media(media_id=post[1],
                                                           media_code=post[0],
                                                           username=user)
                    if like_post:
                        liked += 1
                        self.total_likes += 1
                    else:
                        failed_to_like += 1
                    completion += 1
                    progress_bar(completion=completion,
                             total=total_posts_to_relike,
                             start_time=start_time)
                    time.sleep(1 * random.random())
            print('--Successfully liked in relike session: {}'.format(
                liked))
            insta_logger.info(
                'Successfully liked in relike session: {}'.format(
                    liked))
            print('--Failed to like in relike session: {}'.format(
                failed_to_like))
            insta_logger.info('Failed to like in relike session: {}'.format(
                failed_to_like))
            write_likes(self.total_likes)

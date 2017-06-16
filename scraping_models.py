import time
import sys
import logging
from selenium import webdriver
from urllib.parse import urljoin
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.remote_connection import LOGGER

from insta_logging.insta_logging import insta_logger

__author__ = 'sehlat57'

LOGGER.setLevel(logging.WARNING)


class WebDriver(object):
    def __init__(self):
        self.dcap = dict(DesiredCapabilities.PHANTOMJS)
        self.dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
            "(KHTML, like Gecko) Chrome/15.0.87"
        )
        self.service_args = ['--ignore-ssl-errors=true',
                             '--ssl-protocol=TLSv1']
        self.driver = webdriver.PhantomJS(desired_capabilities=self.dcap,
                                          service_args=self.service_args)
        self.driver.set_page_load_timeout(45)

    def close(self):
        """
        Close web-driver
        :return:
        """
        self.driver.close()


class CrawlFollowing(WebDriver):
    main_url = 'https://www.instagram.com/'

    def __init__(self, user_login, user_password):
        super().__init__()
        self.user_login = user_login
        self.user_password = user_password
        self.user_page = urljoin(self.main_url, user_login) + '/'
        self.login_page = urljoin(self.main_url, 'accounts/login')
        self.followings_list = None

    def login(self, timeout=10, attempts=3):
        """
        Login to account using Selenium and PhantomJS headless browser
        :param timeout: Number of seconds before timing out
        :param attempts: number of attempts to login, default is 3,
        shutting down if failed to login
        :return:
        """
        for attempt in range(attempts):
            print('-Login with Selenium, attempt {} of {}'.format(
                attempt + 1, attempts))
            try:
                self.driver.get(self.login_page)
                WebDriverWait(
                    self.driver, timeout=timeout).until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        '/html/body/span/section/main/div/article/div/'
                        'div[1]/div/form/div[1]/input')))
                login = self.driver.find_element(
                    By.XPATH,
                    '/html/body/span/section/main/div/article/'
                    'div/div[1]/div/form/div[1]/input')
                login.send_keys(self.user_login)
                password = self.driver.find_element(
                    By.XPATH,
                    '/html/body/span/section/main/div/article/div/'
                    'div[1]/div/form/div[2]/input')
                password.send_keys(self.user_password)
                btn = self.driver.find_element(
                    By.XPATH,
                    '/html/body/span/section/main/div/article'
                    '/div/div[1]/div/form/span/button')
                btn.click()
                time.sleep(5)
                if self.driver.current_url == self.main_url:
                    print('--Login successful')
                    insta_logger.info('Selenium: login successful')
                    return 1
                print('--Unable to login with given credentials, attempt {}'
                      ''.format(attempt + 1))
                insta_logger.error('Selenium: login fail, wrong credentials,'
                                   ' attempt #{}'.format(attempt + 1))

            except Exception as e:
                insta_logger.error(
                    'Selenium: login error, Exception: {}, attempt {}'.format(
                        e, attempt + 1))
                print('--Failed. Exception raised.')
        insta_logger.critical('Selenium: unable to login.'
                              'Shutting down')
        insta_logger.info('--------------STOP---------------')
        print('Unable to login. Refer to log file. '
              'Shutting down')
        sys.exit()

    def crawl_folowing_links(self, timeout=15, attempts=3):
        """
        Crawl links from web page using Selenium.
        Paginate hidden links with scroll down script.
        :param timeout: Number of seconds before timing out
        :param attempts: number of attempts to get followings links,
         default is 3, shutting down if failed to get links
        :return: 1 if links extracted from web page successfully
        """
        for attempt in range(attempts):
            print('-Trying to get followings, attempt {} of {}'.format(
                attempt + 1, attempts))
            try:
                self.driver.get(self.user_page)
                time.sleep(3)
                WebDriverWait(
                    self.driver, timeout=timeout).until(
                    EC.presence_of_element_located((
                        By.CLASS_NAME,
                        '_s53mj')))
                total_following_web_elem = self.driver.find_element(
                    By.CSS_SELECTOR,
                    'a[href*="following"] > span')
                total_following = int(total_following_web_elem.text)
                folowing_button = self.driver.find_element(By.CSS_SELECTOR,
                                                           'a[href*='
                                                           '"following"]')
                print('--Total following to extract: {}'.format(
                    total_following))
                folowing_button.click()
                time.sleep(3)
                current_total = len(
                    self.driver.find_elements(By.CLASS_NAME, '_cx1ua'))
                while current_total != total_following:
                    self.driver.execute_script('window.scrollTo(0, document'
                                               '.body.scrollHeight);')
                    time.sleep(2)
                    current_total = len(
                        self.driver.find_elements(By.CLASS_NAME, '_cx1ua'))
                    sys.stdout.write('\r--Total followings'
                                     ' extracted: {}'.format(current_total))
                    sys.stdout.flush()
                sys.stdout.write('\n')
                links_web_elem = self.driver.find_elements(By.CLASS_NAME,
                                                           '_cx1ua')
                links = [link.find_element_by_tag_name(
                    'a').get_attribute('href') for link in links_web_elem]
                if len(links) == total_following:
                    insta_logger.info(
                        'Selenium: Followings links extracted successfully')
                    print('--Followings extracted successfully')
                    self.followings_list = links
                    return 1
                insta_logger.info(
                    'Selenium: failed to extract '
                    'Followings links, attempt #{}'.format(attempt + 1))
                print('--Failed')
            except Exception as e:
                insta_logger.error('Selenium: crawl_following exception '
                                   'raised. Exception: {}, attempt #{}'.format(
                    e, attempt + 1))
                print('--Failed')
        insta_logger.critical(
            'Selenium: unable to get followings. Shutting down')
        insta_logger.info(
            '--------------STOP---------------')
        print(
            '\nUnable to get followings. Refer to log file. Shutting'
            ' down')
        sys.exit()
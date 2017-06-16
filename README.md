# Instagram Like Bot
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/efa2f06951dc44ce9eeed7a056d758ec)](https://www.codacy.com/app/sehlat57/instalike_bot?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=sehlat57/instalike_bot&amp;utm_campaign=Badge_Grade)
[![Python3](https://img.shields.io/badge/python-3.4%2C%203.5%2C%203%2C6-blue.svg)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-3.4.2-brightgreen.svg)](http://www.seleniumhq.org/)
[![requests](https://img.shields.io/badge/requests-2.14.2-yellowgreen.svg)](http://docs.python-requests.org/en/master/)


## Description
Short program written in **Python** that likes post of users you **follow**.
It uses **Selenium** and **PhantomJS** headless WebKit to crawl links of users you follow and **requests** library to like posts using few *hacks* that allow to *GET* user and posts data in json and *POST* data without a use of *official* **Instagram API**.

## Before you start
Consider to use **Python** libraries that have more functionality:

*  [instabot.py](https://github.com/instabot-py/instabot.py)
*  [Instagram-API-python](https://github.com/LevPasha/Instagram-API-python)
*  [InstaPy](https://github.com/timgrossmann/InstaPy)


###### Not to get banned make sure bot doesn't like more than 1000 posts per day

## Installation

- You need **Python 3** to be installed
- Tested on OSX and Debian
---
1. Install the dependencies with [pip](https://pypi.python.org/pypi/pip)
```bash
$ pip install-r requirements.txt
```
2. [Install PhantomJS](phantomjs.org/download.html)

3. Fork/Clone/Download this repo
```bash
$ git clone https://github.com/sehlat57/instalike_bot
```
## Usage
1. Navigate to the directory with ```cd```
```bash
$ cd instalike_bot
```
2. Run the bot with 
```bash 
$ python3 instabot.py -l ACCOUNT_NAME -p PASSWORD
```

##### Optional command line arguments:

- [-h]: help for basic usage
- [-n --number_of_posts] : Number of posts to like (default: 12)
- [--ignore_limit]: add this argument if you want to - ignore limit of 1000 likes per day
(**use it at your own risk**)

##### Full usage example:
```bash
$ python3 instabot.py -l ACCOUNT_NAME -p PASSWORD -n 5 --ignore_limit
```
----

You can add users which posts you **don't want to like**. Just add them to ```ignore_list.txt``` file in the directory.

----
#### Don't forget to check log file for detailed information about bot activity, errors and other information.

## # ToDo

- [ ] Write tests

### Thanks for using

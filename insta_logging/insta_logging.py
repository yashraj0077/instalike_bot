import os
import logging.config
import yaml
from datetime import date

__author__ = 'sehlat57'

logging.getLogger('requests').setLevel(logging.WARNING)
path = os.path.dirname(os.path.abspath(__file__))


def save_to_path():
    """
    Path of the dir to save log file
    :return:
    """
    return os.path.join(path, 'log-{}.txt'.format(date.today()))

# Read logging settings from yaml file
with open(os.path.join(
        path, 'logging_config.yaml'), 'r') as the_conf:
    config_dict = yaml.load(the_conf)

logging.config.dictConfig(config_dict)
insta_logger = logging.getLogger('insta_logger')

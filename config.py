'''
Created on 2017/9/22

@author: dsou
'''
import logging

log = dict(
    version = 1,
    formatters = {
        'f': {'format':
              '%(asctime)s %(name)-25s %(levelname)-8s %(message)s'}
        },
    handlers = {
        'h': {'class': 'logging.StreamHandler',
              'formatter': 'f',
              'level': logging.DEBUG}
        },
    root = {
        'handlers': ['h'],
        'level': logging.DEBUG,
        },
)

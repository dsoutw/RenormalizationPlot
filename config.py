'''
Created on 2017/9/22

@author: dsou
'''
import logging

log = dict(
    version = 1,
    formatters = {
        'default': {'format':
              '%(asctime)s %(name)-20s %(levelname)-8s %(message)s'},
        'defaultfunction': {'format':
              '%(asctime)s %(name)-20s %(levelname)-8s [%(function)s] %(message)s'}

        },
    handlers = {
        'console': {'class': 'logging.StreamHandler',
              'formatter': 'default',
              'level': logging.DEBUG},
        'consolefunction': {'class': 'logging.StreamHandler',
              'formatter': 'defaultfunction',
              'level': logging.DEBUG}
        },
    loggers = {
        'function': {
            'handlers': ['consolefunction'],
            'level': logging.DEBUG,
            'propagate': False
            }
        },
    root = {
        'handlers': ['console'],
        'level': logging.DEBUG,
        },
)

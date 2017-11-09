import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


class Config:
    # flask environ
    APP_NAME = 'Deployment API'
    SECRET_KEY = os.environ['SECRET_KEY']

    # Mongo DB
    DBM_HOST = os.environ['DBM_HOST'].split(',')
    DBM_REPLICASET = os.environ['DBM_REPLICASET']
    DBM_USER = os.environ['DBM_USER']
    DBM_PASSWORD = os.environ['DBM_PASSWORD']
    DBM_DB = os.environ['DBM_DB']

    # AWS
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

    # Deployment URL
    DEPLOYMENT_URL = os.environ['DEPLOYMENT_URL']

    # Logs
    LOG_CONFIG = {'version': 1,
                  'disable_existing_loggers': False,
                  'formatters': {'standard': {'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'},
                                 },
                  'handlers': {'default': {'level': 'DEBUG',
                                           'formatter': 'standard',
                                           'class': 'logging.StreamHandler',
                                           },
                               },
                  'loggers': {'app': {'handlers': ['default'],
                                      'level': 'DEBUG',
                                      'propagate': True,
                                      'formatter': 'standard',
                                      'stream': '/dev/stdout'
}
                              },
                  }

    LOGCONFIG_QUEUE = ['app']
    LOGCONFIG_REQUESTS_ENABLED = True
    LOGCONFIG_REQUESTS_LOGGER = 'app'

    @staticmethod
    def init_app(app):
        pass


class DevelConfig(Config):
    DEBUG = True


class ProdConfig(Config):
    DEBUG = False


config = {
    'devel': DevelConfig,
    'default': DevelConfig,
    'production': ProdConfig
}

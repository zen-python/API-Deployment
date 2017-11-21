import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


class Config(object):
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

    # celery configuration
    CELERY_BROKER_URL = 'redis://redis:6379/0'
    CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
    # CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
    # CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_IGNORE_RESULT = False
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_CONCURRENCY = 3
    CELERY_ACKS_LATE = True
    CELERYD_PREFETCH_MULTIPLIER = 1

    # deployment URL
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
                                      'stream': '/dev/stdout'}
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

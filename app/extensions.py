from app.config import Config
from flask_logconfig import LogConfig
logcfg = LogConfig()

from .ext_aws import AWSExt
aws_ext = AWSExt()

from .ext_dbm import DBMExt
dbm_ext = DBMExt()

from .ext_infra import InfraExt
infra_ext = InfraExt()

from .ext_docker import DockerExt
docker_ext = DockerExt()

from celery import Celery
celery = Celery(broker=Config.CELERY_BROKER_URL,
                backend=Config.CELERY_RESULT_BACKEND)

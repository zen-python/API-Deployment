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

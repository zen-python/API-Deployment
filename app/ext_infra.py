import re
import json
import time
import requests
from flask import current_app


class InfraExt(object):
    """Class treated as flask extension"""
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

    def git_commit_msg(self, payload):
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        instances = payload.pop("groups", None)
        for instance in instances:
            auto_scaling = {'auto_scaling': instance['auto_scaling']}
            for ip_address in instance['instances']:
                url_webhook = f'http://{ip_address}:11560/git_webhook'
                payload = {**payload, **auto_scaling}
                res = requests.post(url_webhook, data=json.dumps(payload), headers=headers)
        return res.status_code

    def docker_commit_msg(self, payload):
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        instances = payload.pop("groups", None)
        for instance in instances:
            auto_scaling = {'auto_scaling': instance['auto_scaling']}
            for ip_address in instance['instances']:
                url_webhook = f'http://{ip_address}:11560/docker_webhook'
                payload = {**payload, **auto_scaling}
                res = requests.post(url_webhook, data=json.dumps(payload), headers=headers)
        return res.status_code

    def run_rsync(self, payload):
        from app.tasks import send_socket_message
        source_path = payload['storage_path']
        command = f'/usr/bin/rsync --progress --stats -avxzl --exclude "*/.git/" -og --chown=www-data:www-data --chmod=D2775,F664 {source_path} /var/www/docker --delete'
        send_socket_message.apply_async(args=[command])

    def update_docker(self, payload):
        from app.tasks import update_docker_task
        repo_image = payload['repo_image']
        tag = payload['tag']
        autoscaling = payload['auto_scaling']
        update_docker_task.apply_async(args=[repo_image, tag, autoscaling])

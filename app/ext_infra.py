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
        # for ip_address in payload['instances']:
        ip_address = '127.0.0.1'
        url_webhook = f'http://{ip_address}:8001/git_webhook'
        res = requests.post(url_webhook, data=json.dumps(payload), headers=headers)
        # if res:
        #    return {'response': res}

    def docker_commit_msg(self, payload):
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        ip_address = '127.0.0.1'
        url_webhook = f'http://{ip_address}:8001/docker_webhook'
        res = requests.post(url_webhook, data=json.dumps(payload), headers=headers)

        # for ip_address in payload[0]['instances']:
        #    url_webhook = f'http://{ip_address}:8011/docker_webhook'
        # res = requests.post(url_webhook, data=payload).json()
        # if res:
        #    return {'response': res}

    def run_rsync(self, payload):
        from app.tasks import run_command
        source_path = payload['storage_path']
        command = f'sudo /usr/bin/rsync --progress --stats -avxzl --exclude "*/.git/" -og --chown=www-data:www-data --chmod=D2775,F664 {source_path} /var/www/docker --delete'
        run_command.apply_async(args=[command])

    def update_docker(self, payload):
        from app.tasks import update_docker_task
        repo_image = payload['repo_image']
        tag = payload['tag']
        update_docker_task.apply_async(args=[repo_image, tag])

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
        for ip_address in payload[0]['instances']:
            ip_address = '127.0.0.1'
            url_webhook = f'http://{ip_address}:8000/git_webhook'
            print(url_webhook)
            res = requests.post(url_webhook, data=json.dumps(payload), headers=headers)
            print(res.status_code)
            #if res:
            #    return {'response': res}

    def docker_commit_msg(self, payload):
        print(payload)
        for ip_address in payload[0]['instances']:
            url_webhook = f'http://{ip_address}:9000/docker_webhook'
            print(url_webhook)
            #res = requests.post(url_webhook, data=payload).json()
            #if res:
            #    return {'response': res}
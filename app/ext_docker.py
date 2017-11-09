import docker
import requests
from flask import current_app


class DockerExt(object):
    """Class treated as flask extension"""
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

    def update_docker(self, repository, post_commands=None):
        DEPLOYMENT_URL = current_app.config['DEPLOYMENT_URL']
        client = docker.APIClient(base_url='unix://var/run/docker.sock')
        container = client.containers(filters={'name': repository})
        image_name = container[0]['Image']
        container_version = image_name.split(':')[1]
        container_id = container[0]['Id']
        image_id = container[0]['ImageID']
        repo_version = requests.get(DEPLOYMENT_URL.format(repository)).text
        if container_version != repo_version:
            client.pull(image_name, repo_version)
            client.stop(container_id)
            client.remove_container(container_id)
            client.remove_image(image_id)
            if post_commands:
                id_exec = client.exec_create(container_id, cmd=post_commands)
                client.exec_start(id_exec['Id'])

import time
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

    def update_docker(self, repo_image, tag, autoscaling):
        from app.tasks import send_socket_message
        DEPLOYMENT_URL = current_app.config['DEPLOYMENT_URL']
        container_version = 'v0'
        client = docker.APIClient(base_url='unix://var/run/docker.sock', version='auto')
        containers = client.containers()
        container_names = []
        container_ids = []
        for container in containers:
            if repo_image in container['Image']:
                image = container['Image']
                image_id = container['ImageID']
                container_version = image.split(':')[1]
                container_names.append(container['Names'][0])
                container_ids.append(container['Id'])
        repo_version = requests.get(DEPLOYMENT_URL.format(repo_image)).text
        if container_version != repo_version and 'dev' not in tag:
            client.pull(repo_image, repo_version)
            for container_id in container_ids:
                client.stop(container_id)
                client.wait(container_id)
                client.remove_container(container_id)
            for container_name in container_names:
                # ejecutar bash de docker_script
                command = f'/storage/{autoscaling}/conf/docker_scripts{container_name}.sh post {repo_image}:{tag}'
                send_socket_message.apply_async(args=[command])
                time.sleep(3)
            client.remove_image(image_id, force=True)
            client.prune_images(filters={'dangling': True})

    def exec_commands(self, deploy_image, commands, path):
        client = docker.APIClient(base_url='unix://var/run/docker.sock', version='auto')
        # ex: image_pull = client.pull('egob/chileatiende_v2:deploy')
        client.pull(deploy_image)
        print(deploy_image, commands, path)
        container = client.create_container(image=deploy_image,
                                            volumes=['/storage'],
                                            host_config=client.create_host_config(
                                            binds={path: {'bind': '/storage',
                                                          'mode': 'rw',}
                                               }
                                           ), working_dir='/storage')
        container_id = container.get('Id')
        client.start(container_id)
        for command in commands:
            id_exec = client.exec_create(container_id, cmd=command)
            client.exec_start(id_exec['Id'])
        client.stop(container_id)
        client.wait(container_id)
        client.remove_container(container_id)

    def restart_docker(self, container_name):
        client = docker.APIClient(base_url='unix://var/run/docker.sock', version='auto')
        container = client.containers(filters={'name': container_name})
        container_id = container[0]['Id']
        client.restart(container_id)

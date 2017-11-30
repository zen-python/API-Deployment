import time
import socket
from celery import states
from celery.contrib import rdb
from subprocess import Popen, PIPE

from app.extensions import celery
from app import create_app, docker_ext, infra_ext, aws_ext


@celery.task(bind=True)
def run_docker_commands_task(self, docker_name, run_commands):
    self.update_state(state='PROGRESS', meta={'message': 'Task in progress.'})
    docker_ext.exec_commands(docker_name, run_commands)
    return {'message': 'Task completed'}


@celery.task(bind=True)
def send_socket_message(self, command):
    HOST = '10.5.0.1'
    PORT = 54321
    self.update_state(state='PROGRESS', meta={'message': 'Task in progress.'})
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(command.encode())
    return {'message': 'Task completed'}


@celery.task(bind=True)
def update_docker_task(self, repo_image, tag, autoscaling):
    app = create_app('default')
    with app.app_context():
        self.update_state(state='PROGRESS', meta={'message': 'Task in progress.'})
        docker_ext.update_docker(repo_image, tag, autoscaling)
        return {'message': 'Task completed'}


@celery.task(bind=True)
def git_message(self, auto_scaling_grp, payload, task_id=None):
    app = create_app('default')
    with app.app_context():
        self.update_state(state='PROGRESS', meta={'message': 'Task in progress'})
        aws_ext.get_instances(auto_scaling_grp, payload, task_id)
        return {'message': 'Task completed'}


@celery.task(bind=True)
def docker_message(self, auto_scaling_grp, payload):
    app = create_app('default')
    with app.app_context():
        self.update_state(state='PROGRESS', meta={'message': 'Task in progress'})
        aws_ext.get_instances(auto_scaling_grp, payload)
        return {'message': 'Task completed'}


@celery.task(bind=True)
def exec_commands(self, deploy_image, commands, path):
    self.update_state(state='PROGRESS', meta={'message': 'Task int progress'})
    docker_ext.exec_commands(deploy_image, commands, path)
    return {'message': 'Task completed'}


@celery.task(bind=True)
def run_command(self, command, timeout=1200):
    if timeout and int(timeout) > 0:
        BASH_TIMEOUT = timeout
    popen = Popen([f"""exec {command}"""], stdout=PIPE, stderr=PIPE, shell=True)
    st_time = time.time()
    wait_time = BASH_TIMEOUT
    while True:
        popen.poll()
        time.sleep(1)
        r_code = popen.returncode
        now = time.time()
        if r_code is not None:
            run_command.update_state(state=states.SUCCESS)
            return {'message': 'Task completed'}
        if (now > (st_time + wait_time)):
            popen.kill()
            run_command.update_state(state=states.FAILURE)
            return {'message': 'Task completed'}
    return {'message': 'Task completed'}

# @celery.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#    sender.add_periodic_task(10.0, run_command.s('date'), name='add every 10')

import re
import datetime
import json
import subprocess
from flask import request
from app import aws_ext, dbm_ext, infra_ext, docker_ext
from app.tasks import run_command, exec_commands, docker_message, git_message

from . import webhook

'''
{
    "repo_full" : "e-gob/traspaso-l54",
    "branch" : {
        "master" : {
            "path" : "/storage/APP_GENERAL/www/docker/traspaso"
        },
        "devel" : {
            "path" : "/storage/APP_GENERAL/www/docker/traspaso-devel"
        }
    },
    "last_update" : ISODate("2017-10-19T19:27:56.983+0000")
}
'''


@webhook.route('/commit', methods=['POST'])
def git_commit():
    '''
    Function: git commit
    Summary: Se recibe el JSON de GitHub cuando se hace commit
    Examples: POST HTTP/1.1 { "json":"json"}
    Attributes:
    Returns:
    '''
    #try:
    # Obtenemos respuesta del commit desde GIT
    git_json = json.loads(request.data)
    # Obtenemos  Nombre Repositorio
    repo_full = git_json['repository']['full_name']
    # Obtenemos Branch ("ref":"refs/heads/devel")
    branch = git_json['ref'].split('/')[2]
    # Deploy
    path = dbm_ext.obtain_path_deploy_code(repo_full, branch)
    # Celery tasks
    command = f'git --work-tree={path} --git-dir={path}/.git pull origin {branch}'
    task_command = run_command.apply_async(args=[command])
    while task_command.status == 'PENDING':
        pass
    task_id = None
    run_commands = dbm_ext.obtain_deploy_image(repo_full)
    if run_commands:
        deploy_image = run_commands['image_deploy']
        commands = run_commands['commands']
        task = exec_commands.apply_async(args=[deploy_image, commands, path])
        task_id = task.id
    auto_scaling_grp = [re.findall('/storage/(.*?)/www', path, re.DOTALL)[0]]
    payload = {'message': 'git', 'repo_full': repo_full, 'branch': branch, 'storage_path': path}
    git_message.apply_async(args=[auto_scaling_grp, payload, task_id])
    # Actualizamos fecha de modificacion del repo
    dbm_ext.update_github_deploy(repo_full, datetime.datetime.now())
    # Logueamos fecha del cambio en la BD
    commit = {"repo_full": repo_full, "branch": branch, "datetime": datetime.datetime.now()}
    dbm_ext.log_commit_github(commit)
    return "True"
    #except:
    #    return "True"


@webhook.route('/commit_docker', methods=['POST'])
def docker_commit():
    '''
    Function: docker commit
    Summary: Se recibe el JSON de DockerHub cuando se hace commit
    Examples: POST HTTP/1.1 { "json":"json"}
    Attributes:
    Returns:
    '''
    tag = json.loads(request.data)['push_data']['tag']
    pusher = json.loads(request.data)['push_data']['pusher']
    repo_name = json.loads(request.data)['repository']['repo_name']
    # Mantenemos lista de Imagenes
    dbm_ext.update_docker_image_info(repo_name, tag, datetime.datetime.now(), pusher)
    # Actualizamos fecha del cambio en la BD
    commit = {"tag": tag, "pusher": pusher, "datetime": datetime.datetime.now(), "repo_name": repo_name}
    dbm_ext.log_commit_docker(commit)
    auto_scaling_grp = dbm_ext.obtain_auto_scaling_grp(repo_name)
    payload = {'message': 'docker', 'repo_image': repo_name, "tag": tag}
    if auto_scaling_grp:
        docker_message.apply_async(args=[auto_scaling_grp, payload])
    return "True"


@webhook.route('/obtain-docker-tag', methods=['GET'])
def obtain_tag_image_docker():
    '''
    Function: obtain tag image
    Summary: Se recibe el JSON de GitHub cuando se hace commit
    Examples: POST HTTP/1.1 { "json":"json"}
    Attributes:
    Returns:
    '''
    try:
        repo = str(request.args.get('repo'))
        tag = dbm_ext.obtain_last_tag_docker_image(repo)
        return str(tag)
    except:
        return "ERROR"


@webhook.route('/obtain-last-update-github', methods=['GET'])
def obtain_last_github_commit():
    '''
    Function: obtain tag image
    Summary: Se recibe el JSON de GitHub cuando se hace commit
    Examples: POST HTTP/1.1 { "json":"json"}
    Attributes:
    Returns:
    '''
    try:
        repo = str(request.args.get('repo'))
        timestamp = dbm_ext.obtain_last_github_commit(repo)
        import time
        return str(int(time.mktime(timestamp.timetuple())))
    except:
        return "ERROR"
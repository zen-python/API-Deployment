import re
import datetime
import json
import subprocess
from flask import request
from app import aws_ext, dbm_ext, infra_ext, logcfg
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
    #subprocess.check_output('git --work-tree=' + path + ' --git-dir=' + path + '/.git pull origin ' + branch, shell=True)
    # Actualizamos fecha de modificacion del repo
    #dbm_client.update_github_deploy(repo_full, datetime.datetime.now())
    # Logueamos fecha del cambio en la BD
    #commit = {"repo_full": repo_full, "branch": branch, "datetime": datetime.datetime.now()}
    #path = dbm_client.log_commit_github(commit)
    auto_scaling_grp = re.findall('/storage/(.*?)/www', path, re.DOTALL)[0]
    instances = aws_ext.get_instances(auto_scaling_grp)
    payload = instances, {'repo_full': repo_full}, {'branch': branch}, {'storage_path': path}
    infra_ext.git_commit_msg(payload)
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
    docker_name = repo_name.split('/')[0]
    # Mantenemos lista de Imagenes
    dbm_ext.update_docker_image_info(repo_name, tag, datetime.datetime.now(), pusher)
    # Actualizamos fecha del cambio en la BD
    commit = {"tag": tag, "pusher": pusher, "datetime": datetime.datetime.now(), "repo_name": repo_name}

    dbm_ext.log_commit_docker(commit)
    auto_scaling_grp = dbm_ext.obtain_auto_scaling_grp(repo_name)
    #auto_scaling_grp = json.loads(request.data)['auto_scaling_grp']['group']
    instances = aws_ext.get_instances(auto_scaling_grp)
    #infra_ext.update_docker(commit.update({'instances': instances}))
    #print(commit)
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
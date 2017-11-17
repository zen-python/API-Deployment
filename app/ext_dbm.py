from flask import current_app
from pymongo import MongoClient
# from remote_pdb import RemotePdb


class DBMExt(object):
    """Class treated as flask extension"""
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        replicaset_name = current_app.config['DBM_REPLICASET']
        host = current_app.config['DBM_HOST']
        db = current_app.config['DBM_DB']
        user = current_app.config['DBM_USER']
        password = current_app.config['DBM_PASSWORD']
        __conn = MongoClient(host=host, replicaset=replicaset_name)
        self.__handle = __conn[db]
        self.__handle.authenticate(user, password)

    def obtain_path_deploy_code(self, repo_full, branch):
        return str(self.__handle.deployment_code.find({"repo_full": repo_full})[0]['branch'][branch]['path'])

    def obtain_last_tag_docker_image(self, repo_name):
        return str(self.__handle.images_docker_hub.find({"repo_name": repo_name})[0]['tag'])

    def obtain_auto_scaling_grp(self, repo_name):
        cursor = self.__handle.images_docker_hub.find({"repo_name": repo_name})[0]
        if 'auto_scaling' in cursor:
            return cursor['auto_scaling']
        return None

    def obtain_last_github_commit(self, repo_full):
        return self.__handle.deployment_code.find({"repo_full": repo_full})[0]['last_update']

    def obtain_deploy_image(self, repo_full):
        cursor = self.__handle.deployment_code.find({"repo_full": repo_full})[0]
        if 'run_commands' in cursor:
            return cursor['run_commands']
        # RemotePdb('127.0.0.1', 4444).set_trace()
        return None

    def obtain_run_commands(self, repo_full):
        return self.__handle.deployment_code.find({"repo_full": repo_full})[0]

    # Update info
    def update_docker_image_info(self, repo_name, tag, datetime, pusher):
        self.__handle.images_docker_hub.update_one({"repo_name": repo_name},
                                                   {"$set": {"datetime": datetime,
                                                             "pusher": pusher,
                                                             "tag": tag}})

    def update_github_deploy(self, repo_full, datetime):
        self.__handle.deployment_code.update_one({"repo_full": repo_full},
                                                 {"$set": {"last_update": datetime}})

    # Logs
    def log_commit_github(self, commit):
        self.__handle.logs_github.insert(commit)

    def log_commit_docker(self, commit):
        self.__handle.logs_dockerhub.insert(commit)

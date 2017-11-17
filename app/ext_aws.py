import backoff
import boto3
import botocore
from flask import current_app
from remote_pdb import RemotePdb


class AWSExt(object):
    """Class treated as flask extension"""
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

    @backoff.on_exception(backoff.expo, botocore.exceptions.ClientError, max_tries=50)
    def get_instances(self, auto_scaling_grp, payload, task_id=None):
        from app.tasks import exec_commands

        AWS_ACCESS_KEY_ID = current_app.config['AWS_ACCESS_KEY_ID']
        AWS_SECRET_ACCESS_KEY = current_app.config['AWS_SECRET_ACCESS_KEY']
        client = boto3.client('autoscaling',
                              aws_access_key_id=AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                              region_name='us-west-2')
        ec2 = boto3.client('ec2',
                           aws_access_key_id=AWS_ACCESS_KEY_ID,
                           aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                           region_name='us-west-2')

        groups = []
        for auto_scaling in auto_scaling_grp:
            res = client.describe_auto_scaling_groups(AutoScalingGroupNames=[auto_scaling])
            for auto_scaling_group in res['AutoScalingGroups']:
                instance_ids = [i for i in auto_scaling_group['Instances']]
                ip_instances = []
                for instance in instance_ids:
                    instance_id = instance['InstanceId']
                    response = ec2.describe_instances(InstanceIds=['{}'.format(instance_id)])
                    ip_instances.append(response['Reservations'][0]['Instances'][0]['NetworkInterfaces']
                                        [0]['PrivateIpAddresses'][0]['PrivateIpAddress'])
                groups.append({'auto_scaling': auto_scaling, 'instances': ip_instances})
        groups = {'groups': groups}
        payload = {**payload, **groups}
        if payload['message'] == 'git':
            self.git_message(payload, task_id)
        else:
            self.docker_message(payload)

    def git_message(self, payload):
        from app import infra_ext
        # RemotePdb('127.0.0.1', 44445).set_trace()
        if task_id:
            task = exec_commands.AsyncResult(task_id)
            while task.status in ('PROGRESS', 'PENDING'):
                pass
            infra_ext.git_commit_msg(payload)
        else:
            infra_ext.git_commit_msg(payload)

    def docker_message(self, payload):
        from app import infra_ext
        infra_ext.docker_commit_msg(payload)

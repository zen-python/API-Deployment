import backoff
import boto3
import botocore
from flask import current_app


class AWSExt(object):
    """Class treated as flask extension"""
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

    @backoff.on_exception(backoff.expo, botocore.exceptions.ClientError, max_tries=15)
    def get_instances(self, auto_scaling_grp):
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

        res = client.describe_auto_scaling_groups(AutoScalingGroupNames=[auto_scaling_grp])

        for auto_scaling_group in res['AutoScalingGroups']:
            instance_ids = [i for i in auto_scaling_group['Instances']]
            ip_instances = []
            for instance in instance_ids:
                instance_id = instance['InstanceId']
                response = ec2.describe_instances(InstanceIds=['{}'.format(instance_id)])
                ip_instances.append(response['Reservations'][0]['Instances'][0]['NetworkInterfaces']
                                    [0]['PrivateIpAddresses'][0]['PrivateIpAddress'])
            return {'auto_scaling': auto_scaling_grp, 'instances': ip_instances}

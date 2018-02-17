import backoff
import boto3
import botocore


@backoff.on_exception(backoff.expo, botocore.exceptions.ClientError, max_tries=50)
def get_instances():
    auto_scaling_grp = ['APP_CERTIFICACION']
    payload = {}
    AWS_ACCESS_KEY_ID = '***REMOVED***'
    AWS_SECRET_ACCESS_KEY = '***REMOVED***'
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
    print(payload)
import logging
import pprint
import boto3

from cloudconstruct.config import conf

log = logging.getLogger(__name__)

AWS_CONFIG = conf.get_config('aws')

def _get_client(service='emr'):
    """Get a boto3 client in the configured region"""
    session = boto3.Session(profile_name=AWS_CONFIG['profile'], region_name=AWS_CONFIG['region'])
    return session.client(service)

def create_cluster(cluster_name: str, min_core: int, max_core: int,
                   min_task: int = 0, max_task: int = 0,
                   master_instance_type: str = "r5.xlarge",
                   core_instance_type: str = "r5.xlarge",
                   task_instance_type: str = "r5.xlarge",
                   ebs_root_volume_size: int = 32,
                   ebs_device_count: int = 4, ebs_device_size_gb: int = 64,
                   temporary: bool = True, jupyter: bool = False) -> str:
    """Create an EMR cluster with the flollowing details/parameters.

    :param str name:
        Name given to newly created cluster

    :param int min_core:
        Minimum number of cores to provision

    :param int max_core:
        Maximum number of ON_DEMAND core nodes that can be provisioned if autoscaling
        is triggered. If ``min_core`` == ``max_core``, autoscaling will be disabled
        for the core nodes.

    :param int min_task:
        Minimum number of tasks to provision

    :param int max_task:
        Maximum number of tasks that can be provisioned if autoscaling
        is triggered. If ``min_task`` == ``max_task``, autoscaling will be disabled
        for the task nodes.

    :param str master_instance_type:
        EC2 instance type for __master node__

    :param str core_instance_type:
        EC2 instance type for __core nodes__

    :param str task_instance_type:
        EC2 instance type for __task nodes__

    :param int ebs_root_volume_size:
        Size of the EBS root volume for all nodes (gigabytes)

    :param int ebs_device_count:
        Number of EBS volumes that will be associated with every core node instance

    :param int ebs_device_size_gb:
        Size for each EBS volume (gigabytes)

    :param bool temporary:
        Flag indicating whether to add a tag to the cluster to indicate the
        cluster shouldn't be terminated programatically.

    :param bool jupyter:
        Start a JupyterHub server or not

    :return: ID of the created cluster
    """
    spec = _get_cluster_detail(cluster_name, min_core, max_core,
                             min_task=min_task, max_task=max_task,
                             master_instance_type=master_instance_type,
                             core_instance_type=core_instance_type,
                             task_instance_type=task_instance_type,
                             ebs_root_volume_size=ebs_root_volume_size,
                             ebs_device_count=ebs_device_count,
                             ebs_device_size_gb=ebs_device_size_gb,
                             spot_price_usd=spot_price_usd, temporary=temporary,
                             jupyter=jupyter)
    log.debug(f"Cluster create spec: {pprint.pformat(spec)}")
    response = _get_client().run_job_flow(**spec)
    return response['JobFlowId']

def _get_cluster_detail(name: str, min_core: int, max_core: int,
                        min_task: int = 0, max_task: int = 0,
                        master_instance_type: str = "r5.xlarge",
                        core_instance_type: str = "r5.xlarge",
                        task_instance_type: str = "r5.xlarge",
                        ebs_root_volume_size: int = 32,
                        ebs_device_count: int = 4, ebs_device_size_gb: int = 64,
                        temporary: bool = True, jupyter: bool = False):
    """ Creates the cluster details in JSON format for CLI submission

    :param str name: The new cluster name

    :param int min_core: the minimum core count to provision

    :param int max_core: the maximum core count to provision

    :param int min_task: the minimum task count to provision

    :param int max_task: the maximum task count to provision

    :param str master_instance_type: EC2 instance type for master

    :param str core_instance_type: EC2 instance type for core

    :param str task_instance_type: EC2 instance type for tasks

    :param int ebs_root_volume_size: root volume size

    :param int ebs_device_count: Number of device volumes

    :param int ebs_device_size_gb device size in GB

    :param bool temporary: Flag indicating if cluster should shutdown at the end of the flow.

    :param bool jupyter: should Jupyter environment JupyterHub be available

    :return: Cluster config in JSON format
    """
    assert max_core >= min_core, f"Max core ({max_core}) must be greater than min core spec ({min_core})"
    assert max_task >= min_task, f"Max task ({max_task}) must be greater than min task spec ({min_task})"

    cluster_type = 'temporary' if temporary else 'permanent'

    cluster_config = {
        'Name': name,
        'Instances': {
            "InstanceFleets": [
                {
                    "InstanceFleetType": "MASTER",
                    "TargetOnDemandCapacity": 1,
                    "InstanceTypeConfigs": [{"InstanceType": "r5.xlarge"}],
                },
                {
                    "InstanceFleetType": "CORE",
                    "TargetOnDemandCapacity": 1,
                    "InstanceTypeConfigs": [{"InstanceType": "r5.xlarge"}],
                },
                {
                    "InstanceFleetType": "TASK",
                    "TargetOnDemandCapacity": max_task,
                    "InstanceTypeConfigs": [{"InstanceType": task_instance_type}],
                },
            ],
            "KeepJobFlowAliveWhenNoSteps": False,
        },
        'LogUri': AWS_CONFIG['emr']['loguri_prefix'],
        'ReleaseLabel': AWS_CONFIG['emr']['releaselabel'],
        'Applications': [{'Name': app} for app in AWS_CONFIG['emr']['applications']]
    }

    return cluster_config
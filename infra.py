"""Work around to accomplish https://github.com/pulumi/pulumi/issues/7048#issuecomment-868100604"""

import pulumi
import custom_config

from pulumi_aws import ec2

"""
This is an example of a intermediate layer, on top of pulumi"s config, to show how one could implement heirarchical configs and directories to help organize multi-tenant configurations in a pulumi project
Below values will be retrieved by keys from 2 different locations:
1. stack specific config located at ./environments/{env}/Pulumi.{env}-{customer_id}.yaml. NOTE: this is the config-file which should be passed to pulumi CLI at time of "up" or "preview" w/ "--config-file" parameter
2. default config located at ./environments/{env}/defaults.yaml

Values will be retrieved from config files in the same order above, meaning the stack specific config will be checked first and the defaults config second.
"""

stack_config_path = "./environments/{env}/{env}-{customer_id}.yaml"
defaults_config_path = "./environments/{env}/defaults.yaml"

"""
Example # 1 - Retrieve value of our EC2 instance type by key, from the stack specific config. an AMI ID from the defaults.yaml file will then be retrieved. 
"""
ec2_config = custom_config.CustomConfig("ec2")
print(f"Retrieving value from {stack_config_path}::instance-type: ", ec2_config.get("instance-type"))

print(f"Retrieving value from {defaults_config_path}::ami-id: ", ec2_config.get("ami-id"))

print(f"Retrieving value from {stack_config_path}::tags: ", ec2_config.require_object("tags"))

"""
Example # 2 - Retrieve integer values of ECS cpu and memory by key, from our defaults config
"""
ecs_config = custom_config.CustomConfig("ecs")
print(f"Retrieving value from {defaults_config_path}::ecs cpu", ecs_config.get_int("cpu"))
print(f"Retrieving value from {defaults_config_path}::ecs memory", ecs_config.get_int("memory"))

"""
Example #3 - Retrieve value of an array of VPCs ID, and subnet IDs
"""
vpc_config = custom_config.CustomConfig("vpc")
print(f"Retrieving value from {defaults_config_path}::vpcid", vpc_config.get("vpcids"))

print(f"Retrieving value from {defaults_config_path}::subnet ids", vpc_config.get_object("subnet-ids"))

"""This should fail if key is not present or if value is not valid boolean"""
print(f"Require bool value from {defaults_config_path}::is-public-facing", vpc_config.require_bool("is-public-facing"))

sg = ec2.SecurityGroup("sec-grp-for-ec2", 
    description="security group",
    ingress=[
        ec2.SecurityGroupIngressArgs(protocol="tcp", from_port=80, to_port=80, cidr_blocks=["0.0.0.0/0"])
    ]
)

ami = ec2.get_ami(
    owners=["amazon"],
    most_recent=True,
    filters=[{"name":"name","values":["amzn-ami-hvm-*"]}]
)

instance = ec2.Instance("instance",
    instance_type=ec2_config.get("instance-type"),
    ami=ami.id,
    vpc_security_group_ids=[sg.id],
)

pulumi.export("ec2_id", instance.id)
pulumi.export("ec2_arn", instance.arn)
"""An AWS Python Pulumi program"""

"""Work around to accomplish https://github.com/pulumi/pulumi/issues/7048#issuecomment-868100604"""

import pulumi
from pulumi.resource import ResourceOptions, ResourceTransformationArgs, ResourceTransformationResult
from pulumi_aws.ec2 import vpc
import custom_config

from pulumi_aws import s3
from pulumi_aws import provider
from pulumi_aws import ec2

def stack_transformation(args: ResourceTransformationArgs):
    pulumi.log.debug(f'Transforming for {args.type_}')
    return ResourceTransformationResult(
        props=args.props,
        opts=ResourceOptions.merge(args.opts, ResourceOptions(
            provider=aws_provider
        ))
    )

def define_aws_provider():
    """
    If one would like to override the aws region specified in the pulumi config, we can use the following
    This will define an aws provider to align with our change in region
    """
    aws_config = custom_config.CustomConfig('aws')

    print('Configuring AWS region: ', aws_config.get_string('region'))

    return provider.Provider("aws_custom_provider", region=aws_config.get_string("region"))

"""
This is an example of a intermediate layer, on top of pulumi's config, to show how one could implement heirarchical configs and directories to help organize multi-tenant configurations in a pulumi project
Below values will be retrieved by keys from 3 different locations:
1. stack specific config located at ./customer_config/{env}/{customer}
2. default config located at ./customer_config/default.config
3. pulumi config located at ./pulumi_config/{stack_name}

Values will be retrieved from config files in the same order above, meaning the stack specific config will be checked first and the pulumi config last.
"""

aws_provider = define_aws_provider()

"""
Register 'stack_transformation' to force all resources to use the explicit user-defined aws-provider
This will ensure our resources use the chosen region
"""
pulumi.runtime.register_stack_transformation(stack_transformation)

"""
Example # 1 - Retrieve value of our EC2 instance type by key, from the customer stack config
"""
ec2_config = custom_config.CustomConfig('ec2')
print('stack config::instance-size: ', ec2_config.get_string('instance-type'))

"""
Example # 2 - Retrieve value of ECS cpu and memory by key, from our default config
"""
ecs_config = custom_config.CustomConfig('ecs')
print('default config::ecs cpu', ecs_config.get_string('cpu'))
print('default config::ecs memory', ecs_config.get_string('memory'))

"""
Example #3 - Retrieve value of VPC ID by key, from our pulumi config
"""
vpc_config = custom_config.CustomConfig("vpc")
print('pulumi_config::vpcid', vpc_config.get_string('vpcid'))

sg = ec2.SecurityGroup('sec-grp-for-ec2', 
    description='security group',
    ingress=[
        ec2.SecurityGroupIngressArgs(protocol='tcp', from_port=80, to_port=80, cidr_blocks=['0.0.0.0/0'])
    ]
)

"""
Note our usage of the 'opts' parameter. Resource get functions, such as 'ec2.get_ami' do not trigger the stack_transformation which deals with setting AWS provider.
Thus, we need to ensure we are explicitly passing the provider using ResourceOptions
"""
ami = ec2.get_ami(
    owners=['amazon'],
    most_recent=True,
    filters=[{"name":"name","values":["amzn-ami-hvm-*"]}],
    opts=ResourceOptions(provider=aws_provider)
)

instance = ec2.Instance('instance',
    instance_type=ec2_config.get_string('instance-type'),
    ami=ami.id,
    vpc_security_group_ids=[sg.id],
)

pulumi.export('ec2_id', instance.id)
pulumi.export('ec2_arn', instance.arn)
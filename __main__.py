
"""Work around to accomplish https://github.com/pulumi/pulumi/issues/7048#issuecomment-868100604"""

import pulumi
import infra

pulumi.export('ec2_id', infra.instance.id)
pulumi.export('ec2_arn', infra.instance.arn)
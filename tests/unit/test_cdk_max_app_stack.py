import aws_cdk as core
import aws_cdk.assertions as assertions
from cdk_max_app.cdk_max_app_stack import CdkMaxAppStack


def test_eks_fargate_created():
    app = core.App()
    stack = CdkMaxAppStack(app, "cdk-max-app")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("Custom::AWSCDK-EKS-FargateProfile", {
        "cluster_name": "max-cluster"
    })

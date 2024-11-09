from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_eks as eks,
    aws_ec2 as ec2,
)
from aws_cdk.lambda_layer_kubectl_v31 import KubectlV31Layer

class CdkMaxAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(
            self, "CdkMaxAppVpc",
        )

        mySecurityGroup = ec2.SecurityGroup(self, "SecurityGroup", vpc=vpc,
                                            description='Allow access to cluster', allow_all_outbound=True)
        
        mySecurityGroup.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), 'allow http from the world');
        mySecurityGroup.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(443), 'allow https access from the world');
        mySecurityGroup.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.icmp_type(-1), 'allow icmp access from the world');
        
        
        cluster = eks.FargateCluster(self, 'max-eks', version=eks.KubernetesVersion.V1_31,
                                     cluster_name='max-cluster', endpoint_access=eks.EndpointAccess.PUBLIC_AND_PRIVATE,
                                     vpc=vpc, authentication_mode=eks.AuthenticationMode.API_AND_CONFIG_MAP,
                                     kubectl_layer=KubectlV31Layer(self, "kubectl"),
                                     alb_controller=eks.AlbControllerOptions(version=eks.AlbControllerVersion.V2_8_2),
                                     )
        
        access_entry = eks.AccessEntry(self, "MyAccessEntry",
            access_policies=[
                eks.AccessPolicy.from_access_policy_name("AmazonEKSClusterAdminPolicy",
                                                         access_scope_type=eks.AccessScopeType.CLUSTER)
            ],
            cluster=cluster,
            principal="arn:aws:iam::771700505853:user/Aws_admin_Sani",
        )

        access_entry1 = eks.AccessEntry(self, "MyEntry",
            access_policies=[
                eks.AccessPolicy.from_access_policy_name("AmazonEKSClusterAdminPolicy",
                                                         access_scope_type=eks.AccessScopeType.CLUSTER)
            ],
            cluster=cluster,
            principal="arn:aws:iam::771700505853:user/terraform-user",
        )

        app_label = {"app": "max-app"}

        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "hello-kubernetes"},
            "spec": {
                "replicas": 3,
                "selector": {"matchLabels": app_label},
                "template": {
                    "metadata": {"labels": app_label},
                    "spec": {
                        "containers": [{
                            "name": "max-app",
                            "image": "max-app-image", # The image deployed in docker would be here
                            "ports": [{"containerPort": 80}]
                        }
                        ]
                    }
                }
            }
        }

        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": "hello-kubernetes"},
            "spec": {
                "type": "LoadBalancer",
                "ports": [{"port": 80, "targetPort": 80}],
                "selector": app_label
            }
        }

        eks.KubernetesManifest(self, "hello-kub",
            cluster=cluster,
            manifest=[deployment, service],
            ingress_alb=True,
            ingress_alb_scheme=eks.AlbScheme.INTERNET_FACING,
            skip_validation=False,
            overwrite=True,
            prune=True,
        )

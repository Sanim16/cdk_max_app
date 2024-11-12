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
        
        cluster.add_fargate_profile("maxappprofile",
                                    selectors=[eks.Selector(namespace="maxapp")]
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

        namespace = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": "maxapp"
            }
        }

        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "hello-kubernetes",
                         "namespace": "maxapp"},
            "spec": {
                "replicas": 3,
                "selector": {"matchLabels": app_label},
                "template": {
                    "metadata": {"labels": app_label},
                    "spec": {
                        "tolerations": [{
                            "key": "eks.amazonaws.com/compute-type",
                            "operator": "Equal",
                            "value": "fargate",
                            "effect": "NoSchedule",
                        }],
                        "containers": [{
                            "name": "max-app",
                            "image": "public.ecr.aws/j0l0w3g7/my-ecr-public-repo:latest", # The image deployed in docker would be here
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
            "metadata": {"name": "hello-kubernetes",
                         "namespace": "maxapp"},
            "spec": {
                "type": "NodePort",
                "ports": [{"port": 80, "targetPort": 80}],
                "selector": app_label
            }
        }

        ingress = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {"namespace": "maxapp",
                         "name": "ingress-maxapp",
                         "annotations": {
                             "alb.ingress.kubernetes.io/scheme": "internet-facing",
                             "alb.ingress.kubernetes.io/target-type": "ip",
                         }
            },
            "spec": {
                "ingressClassName": "alb",
                "rules": [{"http": {"paths": [{"path": "/", "pathType": "Prefix", "backend": {"service": {"name": "hello-kubernetes", "port": {"number": 80}}}}]}}]
            }
        }

        eks.KubernetesManifest(self, "hello-kub",
            cluster=cluster,
            manifest=[namespace, deployment, service, ingress],
            ingress_alb=True,
            ingress_alb_scheme=eks.AlbScheme.INTERNET_FACING,
            skip_validation=False,
            overwrite=True,
            prune=True,
        )

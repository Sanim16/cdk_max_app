# Welcome to AWS CDK Python project!

This project demonstrates the use of AWS CDK to deploy an app to an EKS fargate cluster.

## Architecture Diagram
![Alt text here](image1.png)


The project defines an Amazon EKS cluster with the following configuration:

* Dedicated VPC called `maxappvpc` configured with security groups
* EKS Cluster - The cluster endpoint created by EKS.
* Fargate Profile - Fargate worker nodes managed by EKS.
* KubectlHandler - Lambda function for invoking kubectl commands on the cluster - created by CDK.
* AWS Load Balancer Controller to help manage Elastic Load Balancers for the Kubernetes cluster.
* A Kubernetes deployment with 3 replicas running pods with a container based on the image created from the `./maxapp/` folder.
* A Kubernetes service to expose the app
* A Kubernetes Ingress resource 



This project is set up like a standard Python project.  The initialization process creates
a virtualenv within the project, stored under the .venv directory.  To create the virtualenv
it assumes that there is a `python3` executable in your path with access to the `venv` package.


```
$ python3 -m venv .venv
```

After the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

You can now begin exploring the source code, contained in the `./maxapp/` directory.
There is also a very trivial test included that can be run like this:

```
$ pytest
```


To add additional dependencies, for example other CDK libraries, just add to
your requirements.txt file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!

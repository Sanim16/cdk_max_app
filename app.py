#!/usr/bin/env python3

import aws_cdk as cdk

from cdk_max_app.cdk_max_app_stack import CdkMaxAppStack


app = cdk.App()
CdkMaxAppStack(app, "CdkMaxAppStack")

app.synth()

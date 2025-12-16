#!/usr/bin/env python3
import aws_cdk as cdk

# Import your stack from the correct path
from cdk.stacks.tradeon_core_stack import TradeonCoreStack

app = cdk.App()

# Instantiate your stack
# 'TradeonCoreStack' is the name of the stack in CloudFormation
TradeonCoreStack(app, "TradeonCoreStack", 
    # Optional: Specify environment (Account and Region)
    # env=cdk.Environment(account='YOUR_ACCOUNT_ID', region='YOUR_REGION')
)

app.synth()
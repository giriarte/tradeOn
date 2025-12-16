# tradeon_core/tradeon_core_stack.py

import os.path as path

import aws_cdk as cdk

from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as lambda_, # V2 style for modules like Lambda
)
from aws_cdk.aws_lambda_python_alpha import PythonFunction, PythonLayerVersion
from constructs import Construct

# Calculate the path to the project root (TRADEON directory)
PROJECT_ROOT = path.join(path.dirname(__file__), '..', '..')

class TradeonCoreStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The PythonLayerVersion construct handles bundling dependencies just like PythonFunction,
        # but places them in a reusable layer.
        deps_layer = PythonLayerVersion(
            self,
            "HeavyDependenciesLayer",
            # Point to the directory containing requirements.txt (e.g., your PROJECT_ROOT/main)
            entry=PROJECT_ROOT,
            # This path is where pip installs the packages in the layer
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_12]
        )

        # StrategyMonitorLambda function definition
        tradeon_lambda = PythonFunction(
            self, 
            "StrategyMonitorLambda",
            
            # Use the directory containing the Lambda handler code
            # The path is relative to the directory where 'cdk synth' is run (usually the root)
            entry=PROJECT_ROOT,

            index="StrategyMonitorLambda.py",  # The file containing the handler

            # Specify Python 3.12 (or your preferred version)
            runtime=lambda_.Runtime.PYTHON_3_12,
            
            handler="invoke",
            
            # Optional: Give it a descriptive name
            function_name="StrategyMonitorLambda",
            
            # Add environment variables, memory, timeout, etc. as needed:
            memory_size=2048,
            timeout=cdk.Duration.seconds(60),
            layers=[deps_layer],
            bundling={
                "asset_excludes": [
                    "cdk.out",
                    "aws_cdk",
                    "llvmlite",
                    ".git",
                    ".venv",
                    "venv",
                    "__pycache__",
                    "*.pyc",
                    "node_modules",
                    "tests",
                    "docs",
                    "*.md",
                ]
            }

            # environment={
            #     "ENV_VAR_NAME": "value"
            # }
        )
        
        # NOTE: CDK automatically creates an IAM Role for this function
        # with permissions to write logs to CloudWatch.
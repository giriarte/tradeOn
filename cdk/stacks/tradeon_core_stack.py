# tradeon_core/tradeon_core_stack.py

import os.path as path

import aws_cdk as cdk

from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_dynamodb as dynamodb,
    aws_sns as sns
)
from aws_cdk.aws_lambda_python_alpha import PythonFunction, PythonLayerVersion
from constructs import Construct

# Calculate the path to the project root (TRADEON directory)
PROJECT_ROOT = path.join(path.dirname(__file__), '..', '..')

class TradeonCoreStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # StrategyMonitorLambda function definition
        tradeon_lambda = lambda_.DockerImageFunction(
            self, 
            "StrategyMonitorLambda",
            
            code=lambda_.DockerImageCode.from_image_asset(
                directory=PROJECT_ROOT,
                # Optionally pass build arguments to the Dockerfile if needed
                # build_args={'arg1': 'value'} 
            ),

            function_name="StrategyMonitorLambda",
            
            # Set memory and timeout
            memory_size=1024,
            timeout=cdk.Duration.seconds(120),

            environment={
                "NUMBA_CACHE_DIR": "/tmp"
            }
        )

        # ------------------------------------------------------------------
        # DYNAMODB TABLE DEFINITIONS
        # ------------------------------------------------------------------
        
        # --- 1. Users Table ---
        self.users_table = dynamodb.Table(
            self, 
            "UsersTable",
            table_name="Users",
            partition_key=dynamodb.Attribute(name="email", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="userId", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY, # Use RETAIN for production
        )

        # GSI for brokerId
        self.users_table.add_global_secondary_index(
            index_name="BrokerIdIndex",
            partition_key=dynamodb.Attribute(name="brokerId", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.KEYS_ONLY,
        )
        
        # GSI for phoneNumber
        self.users_table.add_global_secondary_index(
            index_name="PhoneNumberIndex",
            partition_key=dynamodb.Attribute(name="phoneNumber", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.KEYS_ONLY,
        )


        # --- 2. Trades Table ---
        self.trades_table = dynamodb.Table(
            self,
            "TradesTable",
            table_name="Trades",
            partition_key=dynamodb.Attribute(name="userId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="tradeId", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # GSI for status
        self.trades_table.add_global_secondary_index(
            index_name="StatusIndex",
            partition_key=dynamodb.Attribute(name="status", type=dynamodb.AttributeType.STRING),
            # Include the original PK/SK (userId, tradeId) to allow retrieval
            projection_type=dynamodb.ProjectionType.KEYS_ONLY,
        )
        
        # GSI for strategyId
        self.trades_table.add_global_secondary_index(
            index_name="StrategyIdIndex",
            partition_key=dynamodb.Attribute(name="strategyId", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.KEYS_ONLY,
        )
        
        # GSI for brokerId
        self.trades_table.add_global_secondary_index(
            index_name="BrokerIdIndex",
            partition_key=dynamodb.Attribute(name="brokerId", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.KEYS_ONLY,
        )

        
        # --- 3. Strategies Table ---
        self.strategies_table = dynamodb.Table(
            self,
            "StrategiesTable",
            table_name="Strategies",
            partition_key=dynamodb.Attribute(name="userId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="strategyId", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # Grouping all simple GSIs for Strategies table (since they are all single-attribute lookups)
        strategy_gsi_attributes = ["brokerId", "shouldOpenTrades", "shouldNotifyUser", 
                                   "notificationType", "name", "candleInterval"]

        for attr in strategy_gsi_attributes:
            self.strategies_table.add_global_secondary_index(
                index_name=f"{attr}Index",
                partition_key=dynamodb.Attribute(name=attr, type=dynamodb.AttributeType.STRING),
                projection_type=dynamodb.ProjectionType.KEYS_ONLY,
            )

        self.users_table.grant_read_write_data(tradeon_lambda)
        self.trades_table.grant_read_write_data(tradeon_lambda)
        self.strategies_table.grant_read_write_data(tradeon_lambda)

        # ------------------------------------------------------------------
        # SNS TOPIC DEFINITION
        # ------------------------------------------------------------------
        self.trade_notification_topic = sns.Topic(
            self,
            "TradeNotificationTopic",
            topic_name="TradeNotification"
        )

        self.trade_notification_topic.grant_publish(tradeon_lambda)
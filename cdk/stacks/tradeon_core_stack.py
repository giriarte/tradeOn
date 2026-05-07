# tradeon_core/tradeon_core_stack.py

import os.path as path

import aws_cdk as cdk

from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_lambda_event_sources as lambda_event_sources,
    aws_dynamodb as dynamodb,
    aws_sns as sns,
    aws_sqs as sqs,
    aws_events as events,
    aws_events_targets as targets,
)
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
                "NUMBA_CACHE_DIR": "/tmp",
                "SNS_TOPIC_ARN": f"arn:aws:sns:us-east-1:{self.account}:TradeNotification",
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

        # GSI for userId
        self.users_table.add_global_secondary_index(
            index_name="USERS_USERID_GSI",
            partition_key=dynamodb.Attribute(name="userId", type=dynamodb.AttributeType.STRING),
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

        # --- 4. Alerts Table ---
        self.alerts_table = dynamodb.Table(
            self,
            "AlertsTable",
            table_name="Alerts",
            partition_key=dynamodb.Attribute(name="strategyId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="alertId", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            time_to_live_attribute="ttl",
        )

        # GSI for userId
        self.alerts_table.add_global_secondary_index(
            index_name="UserIdIndex",
            partition_key=dynamodb.Attribute(name="userId", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.KEYS_ONLY,
        )

        # GSI for alertTime
        self.alerts_table.add_global_secondary_index(
            index_name="AlertTimeIndex",
            partition_key=dynamodb.Attribute(name="alertTime", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.KEYS_ONLY,
        )

        # --- 5. Subscriptions Table ---
        # Users table carries an `activeSubscriptionId` attribute (schemaless)
        # that points to the current active subscription for fast lookups.
        self.subscriptions_table = dynamodb.Table(
            self,
            "SubscriptionsTable",
            table_name="Subscriptions",
            partition_key=dynamodb.Attribute(name="userId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="subscriptionId", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            time_to_live_attribute="ttl",
        )

        # GSI: direct lookup by subscriptionId (e.g. from a webhook or payment event)
        self.subscriptions_table.add_global_secondary_index(
            index_name="SubscriptionIdIndex",
            partition_key=dynamodb.Attribute(name="subscriptionId", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.ALL,
        )

        # GSI: list all subscriptions by status (ALL projection required so BillRunLambda
        # can filter on `type`, `currentPeriodStart`, and `currentPeriodEnd` in one query)
        self.subscriptions_table.add_global_secondary_index(
            index_name="StatusIndex",
            partition_key=dynamodb.Attribute(name="status", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.ALL,
        )

        # --- 6. PaymentMethods Table ---
        # Stores a user's saved payment methods (cards, PayPal accounts, crypto wallets).
        # Payments reference a paymentMethodId from this table instead of embedding details.
        self.payment_methods_table = dynamodb.Table(
            self,
            "PaymentMethodsTable",
            table_name="PaymentMethods",
            partition_key=dynamodb.Attribute(name="userId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="paymentMethodId", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            time_to_live_attribute="ttl",
        )

        # GSI: direct lookup by paymentMethodId (e.g. resolving a reference from a Payment item)
        self.payment_methods_table.add_global_secondary_index(
            index_name="PaymentMethodIdIndex",
            partition_key=dynamodb.Attribute(name="paymentMethodId", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.ALL,
        )

        # GSI: list all methods of a given type (e.g. all CRYPTO methods)
        self.payment_methods_table.add_global_secondary_index(
            index_name="TypeIndex",
            partition_key=dynamodb.Attribute(name="type", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.KEYS_ONLY,
        )

        # --- 7. Invoices Table ---
        self.invoices_table = dynamodb.Table(
            self,
            "InvoicesTable",
            table_name="Invoices",
            partition_key=dynamodb.Attribute(name="userId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="invoiceId", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            time_to_live_attribute="ttl",
        )

        # GSI: all invoices for a subscription in chronological order
        self.invoices_table.add_global_secondary_index(
            index_name="SubscriptionIdIndex",
            partition_key=dynamodb.Attribute(name="subscriptionId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="createdAt", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.ALL,
        )

        # GSI: find all open / uncollectible invoices across the system (ALL projection
        # required so InvoiceCollectionLambda can read dueDate and subscriptionId
        # directly from the index without extra get_item round-trips)
        self.invoices_table.add_global_secondary_index(
            index_name="StatusIndex",
            partition_key=dynamodb.Attribute(name="status", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.ALL,
        )

        # --- 8. Payments Table ---
        self.payments_table = dynamodb.Table(
            self,
            "PaymentsTable",
            table_name="Payments",
            partition_key=dynamodb.Attribute(name="userId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="paymentId", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            time_to_live_attribute="ttl",
        )

        # GSI: all payments for a subscription ordered by createdAt
        self.payments_table.add_global_secondary_index(
            index_name="SubscriptionIdIndex",
            partition_key=dynamodb.Attribute(name="subscriptionId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="createdAt", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.ALL,
        )

        # GSI: find pending / failed payments across the system
        self.payments_table.add_global_secondary_index(
            index_name="StatusIndex",
            partition_key=dynamodb.Attribute(name="status", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.KEYS_ONLY,
        )

        self.users_table.grant_read_write_data(tradeon_lambda)
        self.trades_table.grant_read_write_data(tradeon_lambda)
        self.strategies_table.grant_read_write_data(tradeon_lambda)
        self.alerts_table.grant_read_write_data(tradeon_lambda)
        self.subscriptions_table.grant_read_write_data(tradeon_lambda)
        self.payment_methods_table.grant_read_write_data(tradeon_lambda)
        self.invoices_table.grant_read_write_data(tradeon_lambda)
        self.payments_table.grant_read_write_data(tradeon_lambda)

        # ------------------------------------------------------------------
        # BILL RUN LAMBDA
        # ------------------------------------------------------------------

        bill_run_lambda = lambda_.DockerImageFunction(
            self,
            "BillRunLambda",
            code=lambda_.DockerImageCode.from_image_asset(
                directory=PROJECT_ROOT,
                cmd=["BillRunLambda.handler"],
            ),
            function_name="BillRunLambda",
            memory_size=512,
            timeout=cdk.Duration.minutes(5),
        )

        # Read subscriptions, write invoices
        self.subscriptions_table.grant_read_data(bill_run_lambda)
        self.invoices_table.grant_write_data(bill_run_lambda)

        # Trigger on the 1st of every month at 00:00 UTC — disabled by default
        bill_run_rule = events.Rule(
            self,
            "BillRunSchedule",
            rule_name="BillRunMonthlySchedule",
            schedule=events.Schedule.cron(minute="0", hour="0", day="1", month="*", year="*"),
            enabled=False,
        )
        bill_run_rule.add_target(targets.LambdaFunction(bill_run_lambda))

        # ------------------------------------------------------------------
        # INVOICE COLLECTION LAMBDA
        # ------------------------------------------------------------------

        invoice_collection_lambda = lambda_.DockerImageFunction(
            self,
            "InvoiceCollectionLambda",
            code=lambda_.DockerImageCode.from_image_asset(
                directory=PROJECT_ROOT,
                cmd=["InvoiceCollectionLambda.handler"],
            ),
            function_name="InvoiceCollectionLambda",
            memory_size=512,
            timeout=cdk.Duration.minutes(5),
        )

        # Read invoices, write invoices + subscriptions + users
        self.invoices_table.grant_read_write_data(invoice_collection_lambda)
        self.subscriptions_table.grant_read_write_data(invoice_collection_lambda)
        self.users_table.grant_read_write_data(invoice_collection_lambda)

        # Trigger every day at 01:00 UTC (after BillRun's midnight window) — disabled by default
        invoice_collection_rule = events.Rule(
            self,
            "InvoiceCollectionSchedule",
            rule_name="InvoiceCollectionDailySchedule",
            schedule=events.Schedule.cron(minute="0", hour="1", day="*", month="*", year="*"),
            enabled=False,
        )
        invoice_collection_rule.add_target(targets.LambdaFunction(invoice_collection_lambda))

        # ------------------------------------------------------------------
        # SNS TOPIC DEFINITION
        # ------------------------------------------------------------------
        self.trade_notification_topic = sns.Topic(
            self,
            "TradeNotificationTopic",
            topic_name="TradeNotification"
        )

        self.trade_notification_topic.grant_publish(tradeon_lambda)

        # ------------------------------------------------------------------
        # STRATEGY MONITOR QUEUE
        # ------------------------------------------------------------------
        self.strategy_monitor_queue = sqs.Queue(
            self,
            "StrategyMonitorQueue",
            queue_name="StrategyMonitorQueue",
            visibility_timeout=cdk.Duration.seconds(120),  # must be >= lambda timeout
        )

        # Grant StrategyMonitorLambda permission to consume messages
        self.strategy_monitor_queue.grant_consume_messages(tradeon_lambda)

        # Trigger StrategyMonitorLambda when messages arrive in the queue
        tradeon_lambda.add_event_source(
            lambda_event_sources.SqsEventSource(
                self.strategy_monitor_queue,
                batch_size=1,
            )
        )

        # ------------------------------------------------------------------
        # ACTIVE SUBSCRIPTION GATHERER LAMBDA
        # ------------------------------------------------------------------

        active_subscription_gatherer_lambda = lambda_.DockerImageFunction(
            self,
            "ActiveSubscriptionGathererLambda",
            code=lambda_.DockerImageCode.from_image_asset(
                directory=PROJECT_ROOT,
                cmd=["ActiveSubscriptionGathererLambda.handler"],
            ),
            function_name="ActiveSubscriptionGathererLambda",
            memory_size=512,
            timeout=cdk.Duration.minutes(5),
        )

        # Read active subscriptions and user details
        self.subscriptions_table.grant_read_data(active_subscription_gatherer_lambda)
        self.users_table.grant_read_data(active_subscription_gatherer_lambda)

        # Send gathered user messages to StrategyMonitorQueue
        self.strategy_monitor_queue.grant_send_messages(active_subscription_gatherer_lambda)

        # Trigger every minute — disabled by default
        active_subscription_gatherer_rule = events.Rule(
            self,
            "ActiveSubscriptionGathererSchedule",
            rule_name="ActiveSubscriptionGathererMinuteSchedule",
            schedule=events.Schedule.rate(cdk.Duration.minutes(1)),
            enabled=False,
        )
        active_subscription_gatherer_rule.add_target(
            targets.LambdaFunction(active_subscription_gatherer_lambda)
        )
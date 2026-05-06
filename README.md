# Tradeon

## Prerequisites

- Python 3.13
- AWS CLI configured with valid credentials (`aws configure`)
- Node.js + AWS CDK CLI (`npm install -g aws-cdk`)
- Docker (for CDK deployment)

Install Python dependencies:

```bash
pip install -r requirements.txt
```

---

## Local Testing

All lambdas talk to the real AWS DynamoDB/SQS/SNS — make sure your AWS credentials are set and point to the correct environment before running locally.

---

### StrategyMonitorLambda

**What it does:** For a given user, fetches their active trading strategies from DynamoDB, downloads live OHLCV data from Binance for each configured symbol, and runs the strategy's signal logic. If a buy/sell signal fires (and the strategy is not in cooldown), it publishes a notification to the `TradeNotification` SNS topic and records the alert in the `Alerts` table.

It also supports a **test mode** that skips live data and replays historical CSV files from `tests/historicalData5m/crypto/`, plotting signals on a chart — useful for validating strategy logic without touching AWS infrastructure.

**To run locally:**

1. Uncomment the block at the bottom of [StrategyMonitorLambda.py](StrategyMonitorLambda.py):

```python
user_payload = {
    "email": "your@email.com",
    "userId": "your-user-id",
    "testMode": True   # set to False for the live Binance flow
}

invoke(user_payload, None)
```

2. Run it:

```bash
python StrategyMonitorLambda.py
```

- With `testMode: True` — reads CSVs from `tests/historicalData5m/crypto/` and opens an interactive chart.
- With `testMode: False` — downloads live data from Binance and sends real SNS notifications.

> Remember to re-comment the block before deploying.

---

### ActiveSubscriptionGathererLambda

**What it does:** Runs on a 1-minute EventBridge schedule. Queries the `Subscriptions` table for all users with an `ACTIVE` subscription, looks up their email from the `Users` table, and sends one SQS message per user to the `StrategyMonitorQueue`. This is the entry point of the monitoring pipeline — it fans out to `StrategyMonitorLambda`.

**To run locally:**

Add this block at the bottom of [ActiveSubscriptionGathererLambda.py](ActiveSubscriptionGathererLambda.py) and run it:

```python
if __name__ == "__main__":
    result = handler({}, None)
    print(result)
```

```bash
python ActiveSubscriptionGathererLambda.py
```

This will queue real SQS messages, which will trigger `StrategyMonitorLambda` if it is deployed.

---

### InvoiceCollectionLambda

**What it does:** Runs daily. Scans all `OPEN` invoices in the `Invoices` table and finds those whose `dueDate` has passed. For each expired invoice it: marks the invoice `UNCOLLECTIBLE`, marks the associated subscription `PAST_DUE`, provisions a new `FREE` subscription for the user, and updates the user's `activeSubscriptionId` to the new free subscription.

**To run locally:**

Add this block at the bottom of [InvoiceCollectionLambda.py](InvoiceCollectionLambda.py) and run it:

```python
if __name__ == "__main__":
    result = handler({}, None)
    print(result)
```

```bash
python InvoiceCollectionLambda.py
```

This will write real changes to DynamoDB — seed test data first or point to a non-production environment.

---

### BillRunLambda

**What it does:** Runs on the 1st of every month. Queries all `ACTIVE` subscriptions of type `STANDARD` or `PRO`, computes the amount due based on the pricing table (`STANDARD: $9.99`, `PRO: $29.99`), and creates an `OPEN` invoice in the `Invoices` table for each one. It does not charge cards — it only generates the invoice record that `InvoiceCollectionLambda` will later enforce.

**To run locally:**

Add this block at the bottom of [BillRunLambda.py](BillRunLambda.py) and run it:

```python
if __name__ == "__main__":
    result = handler({}, None)
    print(result)
```

```bash
python BillRunLambda.py
```

This will write real invoice records to DynamoDB.

---

### backtest.py

**What it does:** Runs a full historical backtest using the [`backtesting`](https://github.com/kernc/backtesting.py) library. It reads OHLCV CSV files from `tests/historicalData5m/fxify/`, replays the `ThreeGreenCandlesRsi` strategy bar-by-bar, and simulates trade execution with configurable cash, leverage, and commission. At the end it prints a performance summary (return %, win rate, Sharpe ratio, etc.) per file and saves HTML chart files to `plots/`.

**To run locally:**

```bash
python tests/backtest.py
```

Make sure `tests/historicalData5m/fxify/` contains at least one `.csv` file with columns: `Open`, `High`, `Low`, `Close`. The index should be timestamps in the format `%d.%m.%Y %H:%M:%S.%f`.

The `plots/` directory must exist before running:

```bash
mkdir plots
```

---

## Deploy to AWS with CDK

All infrastructure (Lambdas, DynamoDB tables, SQS queue, SNS topic, EventBridge rules) is defined in [cdk/stacks/tradeon_core_stack.py](cdk/stacks/tradeon_core_stack.py). All lambdas are deployed as Docker image functions using the [Dockerfile](Dockerfile) at the project root.

### First-time setup

Bootstrap CDK in your AWS account (only needed once per account/region):

```bash
cdk bootstrap
```

### Synthesize (optional — preview the CloudFormation template)

```bash
cdk synth
```

### Deploy

```bash
cdk deploy
```

CDK will build the Docker image, push it to ECR, and deploy the full stack. The EventBridge schedules for `ActiveSubscriptionGathererLambda`, `BillRunLambda`, and `InvoiceCollectionLambda` are created **disabled by default** — enable them manually in the AWS Console or via CDK once you're ready.

### Tear down

```bash
cdk destroy
```

> DynamoDB tables use `RemovalPolicy.DESTROY` — all data will be deleted on stack teardown.

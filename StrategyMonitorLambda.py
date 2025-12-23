import yfinance as yf
import sys
import os
import plotly.graph_objects as go
import numpy as np
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import typing as t
import pandas_ta as ta
from strategies.StrategyBuilder import create_strategy

dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table('Users')
strategies_table = dynamodb.Table('Strategies')
# Initialize the SNS client
sns_client = boto3.client('sns', region_name='us-east-1')
TOPIC_ARN = "arn:aws:sns:us-east-1:542557037063:TradeNotification"

# --- System Path Setup (Keep as is) ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- Imports (Keep as is) ---
from indicators.rsi import RSI
from indicators.nRedCandles import NRedCandles
from strategies.strategy import TradeStrategy
from strategies.position import Position
from indicators.constants import ( 
    CLOSE_COLUMN,
    OPEN_COLUMN,
    N_CANDLES_LENGTH,
    N_CANDLES_OPERATION,
    RSI_LENGTH,
    RSI_BUY_THRESHOLD,
    RSI_SELL_THRESHOLD
)

# --- Helper Functions (Keep as is) ---
def pointpos(x, xsignal):
    if x[xsignal] == 2:
        return x['High'] + 1e-4
    elif x[xsignal] == 1:
        return x['Low'] - 1e-4
    else:
        return np.nan

def plot_with_signal(dfpl):
    # 1. Setup Data
    dfpl = dfpl.copy()
    
    # Calculate EMAs (as per your snippet)
    dfpl['EMA_9'] = ta.ema(dfpl[CLOSE_COLUMN], length=15)
    dfpl['EMA_21'] = ta.ema(dfpl[CLOSE_COLUMN], length=50)
    
    # Calculate Bollinger Bands (Length 20, Std Dev 2)
    bb_length = 20
    bb_std = 2.0
    bb = ta.bbands(dfpl[CLOSE_COLUMN], length=bb_length, std=bb_std)
    
    # Extract BB columns (naming convention: BBL_length_std)
    dfpl['BBL'] = bb[f'BBL_{bb_length}_{bb_std}_{bb_std}']
    dfpl['BBM'] = bb[f'BBM_{bb_length}_{bb_std}_{bb_std}']
    dfpl['BBU'] = bb[f'BBU_{bb_length}_{bb_std}_{bb_std}']

    fig = go.Figure()

    # 2. Add Bollinger Bands (Adding these first so they sit behind candlesticks)
    # Upper Band
    fig.add_trace(go.Scatter(
        x=dfpl.index, y=dfpl['BBU'],
        line=dict(color='rgba(173, 216, 230, 0.4)', width=1),
        name="BB Upper"
    ))

    # Lower Band with Fill
    fig.add_trace(go.Scatter(
        x=dfpl.index, y=dfpl['BBL'],
        line=dict(color='rgba(173, 216, 230, 0.4)', width=1),
        fill='tonexty', # Fills the area between BBU and BBL
        fillcolor='rgba(173, 216, 230, 0.1)', 
        name="BB Lower"
    ))

    # 3. Add Candlesticks
    fig.add_trace(go.Candlestick(
        x=dfpl.index,
        open=dfpl[OPEN_COLUMN],
        high=dfpl['High'],
        low=dfpl['Low'],
        close=dfpl[CLOSE_COLUMN],
        name="Candlesticks"
    ))

    # 4. Add the EMA Lines
    fig.add_trace(go.Scatter(
        x=dfpl.index, y=dfpl['EMA_21'], 
        line=dict(color='yellow', width=1.5), 
        name="EMA 21"
    ))

    fig.add_trace(go.Scatter(
        x=dfpl.index, y=dfpl['EMA_9'], 
        line=dict(color='orange', width=1.5), 
        name="EMA 9"
    ))

    # 5. Add the Signals (Markers)
    fig.add_scatter(
        x=dfpl.index, y=dfpl['pointpos'], 
        mode="markers",
        marker=dict(size=10, color="MediumPurple", symbol="diamond"),
        name="Signal"
    )

    # 6. Layout styling
    fig.update_layout(
        autosize=False,
        width=1200,
        height=800, 
        paper_bgcolor='black',
        plot_bgcolor='black',
        legend=dict(font=dict(color="white"))
    )
    
    fig.update_xaxes(gridcolor='#333333', zeroline=False)
    fig.update_yaxes(gridcolor='#333333', zeroline=False)
    
    fig.show()

def plotResults(data):
    data['pointpos'] = data.apply(lambda row: pointpos(row, "strategy_output"), axis=1)
    plot_with_signal(data)

# ====================================================================
# --- NEW: Main Logic Function ---
# ====================================================================

should_plot = True

def invoke(event, context):
    # 1. Extract identifiers from the payload
    email = event.get('email')
    user_id = event.get('userId')
    testMode = event.get('testMode')

    # Data Download and Cleanup
    print("Downloading data...")
    raw_data = yf.download(tickers='BTC-USD', period='1y', interval='1d')
    # Clean up column names (e.g., ('Close', '') -> 'Close')
    raw_data.columns = [col[0] if isinstance(col, tuple) else col for col in raw_data.columns]

    if not email or not user_id:
        return {"statusCode": 400, "body": "Missing email or userId in payload"}

    user_details = getUserDetails(email, user_id)

    user_strategies = getUserStrategies(email, user_id)

    # --- Transform to Objects ---
    trade_strategies: t.List[TradeStrategy] = []

    for item in user_strategies:
        try:
            strategy_obj = create_strategy(item)
            trade_strategies.append(strategy_obj)
        except Exception as hydration_error:
            print(f"Failed to hydrate strategy {item.get('name')}: {hydration_error}")
            # Continue to next strategy even if one fails
            continue

    if testMode:
        print("Running in test mode...")
        doTestMode(raw_data, trade_strategies)
        return {"statusCode": 200, "body": "Test mode execution complete."}

    # Real flow, in case testMode is not active...
    for strategy in trade_strategies:
        # raw_data[0:141] is to force generate a signal. Replace it with raw_data for full dataset
        strategy_position_output = strategy.evaluate(raw_data[0:141], None)
        
        if strategy_position_output:
            alert_message = f"Strategy {strategy.name} generated a signal: {strategy_position_output.type}"
            print(alert_message)
            
            try:
                # Publish to the SNS Topic
                response = sns_client.publish(
                    TopicArn=TOPIC_ARN,
                    Message=alert_message,
                    Subject=f"Trading Alert: {strategy.name}"
                )
                print(f"Notification sent! Message ID: {response['MessageId']}")
                
            except ClientError as e:
                print(f"Failed to send notification: {e.response['Error']['Message']}")

        else:
            print(f"Strategy {strategy.name} did not generate any signal.")


def doTestMode(raw_data, trade_strategies):
    for strategy in trade_strategies:
        strategy_output = [0] * len(raw_data)
        for i in range(0, len(raw_data)):
            # Pass the data up to the current bar
            df = raw_data.iloc[0:i] 
            
            strategy_position_output = strategy.evaluate(df, None)
            
            if strategy_position_output:
                # Store the type (e.g., 1 for Buy, 2 for Sell)
                strategy_output[i] = strategy_position_output.type
                print(f"Index {i}: Strategy {strategy.name} generated signal {strategy_position_output.type}")
            else:
                strategy_output[i] = 0 # Use 0 instead of None for easier plotting/analysis
                
        raw_data["strategy_output"] = strategy_output
        print("Single stratey test complete.")

        # 5. Plotting Results
        if should_plot:
            print("Plotting results...")
            plotResults(raw_data)
        print(raw_data)



def getUserStrategies(email, user_id):
    try:
        strategies_response = strategies_table.query(
            KeyConditionExpression=Key('userId').eq(user_id)
        )
        strategies_list = strategies_response.get('Items', [])

        # Business logic goes here
        print(f"Fetched {len(strategies_list)} strategies for user {email}")

        return strategies_list
    except Exception as e:
        print(f"Error accessing DynamoDB: {str(e)}")
        return {"statusCode": 500, "body": "Internal Server Error"}

def getUserDetails(email, user_id):
    try:
        user_response = users_table.get_item(
            Key={
                'email': email,
                'userId': user_id
            }
        )
        user_details = user_response.get('Item') # This is your UserDetails object
        
        if not user_details:
            return {"statusCode": 404, "body": "User not found"}
        
        return user_details
    except Exception as e:
        print(f"Error accessing DynamoDB: {str(e)}")
        return {"statusCode": 500, "body": "Internal Server Error"}


user_payload = {
    "email": "a.g.iriarte@gmail.com",
    "userId": "12345",
    "testMode": True
}

invoke(user_payload, None)
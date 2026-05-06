import json
import boto3
from boto3.dynamodb.conditions import Key

from model.subscription import SubscriptionStatus

dynamodb = boto3.resource('dynamodb')
sqs = boto3.client('sqs')

subscriptions_table = dynamodb.Table('Subscriptions')
users_table = dynamodb.Table('Users')

QUEUE_NAME = 'StrategyMonitorQueue'


def handler(event, context):
    queue_url = sqs.get_queue_url(QueueName=QUEUE_NAME)['QueueUrl']

    subscriptions = _get_active_subscriptions()
    print(f"[INFO] Found {len(subscriptions)} active subscription(s).")

    sent, errors = 0, 0

    for sub in subscriptions:
        user_id = sub['userId']
        try:
            email = _get_user_email(user_id)
            if not email:
                print(f"[WARN] No user found for userId={user_id}, skipping.")
                continue

            sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps({'email': email, 'userId': user_id}),
            )
            sent += 1
            print(f"[INFO] Queued userId={user_id} email={email}.")
        except Exception as exc:
            errors += 1
            print(f"[ERROR] Failed to queue userId={user_id}: {exc}")

    print(f"[INFO] Done — sent: {sent}, errors: {errors}.")
    return {'sent': sent, 'errors': errors}


def _get_active_subscriptions() -> list[dict]:
    active = []
    last_key = None

    while True:
        kwargs = {
            'IndexName': 'StatusIndex',
            'KeyConditionExpression': Key('status').eq(SubscriptionStatus.ACTIVE.value),
        }
        if last_key:
            kwargs['ExclusiveStartKey'] = last_key

        response = subscriptions_table.query(**kwargs)
        active.extend(response.get('Items', []))

        last_key = response.get('LastEvaluatedKey')
        if not last_key:
            break

    return active


def _get_user_email(user_id: str) -> str | None:
    response = users_table.query(
        IndexName='USERS_USERID_GSI',
        KeyConditionExpression=Key('userId').eq(user_id),
        Limit=1,
    )
    items = response.get('Items', [])
    return items[0]['email'] if items else None

if __name__ == "__main__":
    result = handler({}, None)
    print(result)
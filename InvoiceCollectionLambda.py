import uuid
import boto3
from datetime import datetime, timezone

from boto3.dynamodb.conditions import Key
from model.subscription import ttl_three_years

from model.invoice import InvoiceStatus
from model.subscription import SubscriptionType, SubscriptionStatus

# ---------------------------------------------------------------------------
# DynamoDB resources
# ---------------------------------------------------------------------------

dynamodb        = boto3.resource('dynamodb')
invoices_table  = dynamodb.Table('Invoices')
subs_table      = dynamodb.Table('Subscriptions')
users_table     = dynamodb.Table('Users')

# ---------------------------------------------------------------------------
# Handler
# ---------------------------------------------------------------------------

def handler(event, context):
    """
    Invoice collection entry point.
    Runs daily (EventBridge schedule). For every OPEN invoice whose dueDate
    has passed:
      1. Mark the invoice UNCOLLECTIBLE.
      2. Mark the associated subscription PAST_DUE.
      3. Provision a new FREE subscription for the user and make it ACTIVE.
      4. Update the user's activeSubscriptionId to the new FREE subscription.
    """
    now     = datetime.now(timezone.utc)
    now_iso = now.isoformat()

    expired_invoices = _get_open_expired_invoices(now_iso)
    print(f"[INFO] Found {len(expired_invoices)} expired open invoice(s).")

    processed, errors = 0, 0

    for invoice in expired_invoices:
        invoice_id      = invoice['invoiceId']
        user_id         = invoice['userId']
        subscription_id = invoice['subscriptionId']
        try:
            _mark_invoice_uncollectible(user_id, invoice_id, now_iso)
            _mark_subscription_past_due(user_id, subscription_id, now_iso)
            free_sub_id = _provision_free_subscription(user_id, now_iso)
            _update_user_active_subscription(user_id, free_sub_id, now_iso)

            processed += 1
            print(f"[INFO] Processed expired invoice {invoice_id} for userId={user_id}. "
                  f"New free subscription: {free_sub_id}.")
        except Exception as exc:
            errors += 1
            print(f"[ERROR] Failed to process invoice {invoice_id} "
                  f"for userId={user_id}: {exc}")

    print(f"[INFO] Invoice collection complete — processed: {processed}, errors: {errors}.")
    return {'processed': processed, 'errors': errors}

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_open_expired_invoices(now_iso: str) -> list[dict]:
    """
    Returns all OPEN invoices whose dueDate is before now, via a paginated
    query on the Invoices StatusIndex (ALL projection).
    Client-side date filtering is used because DynamoDB doesn't support
    range filters on non-key attributes in a KeyConditionExpression.
    """
    results  = []
    last_key = None

    while True:
        kwargs = {
            'IndexName': 'StatusIndex',
            'KeyConditionExpression': Key('status').eq(InvoiceStatus.OPEN.value),
        }
        if last_key:
            kwargs['ExclusiveStartKey'] = last_key

        response = invoices_table.query(**kwargs)

        for item in response.get('Items', []):
            if item.get('dueDate', '') < now_iso:
                results.append(item)

        last_key = response.get('LastEvaluatedKey')
        if not last_key:
            break

    return results


def _mark_invoice_uncollectible(user_id: str, invoice_id: str, now_iso: str) -> None:
    # ConditionExpression guards against a race with a concurrent payment settlement
    invoices_table.update_item(
        Key={'userId': user_id, 'invoiceId': invoice_id},
        UpdateExpression='SET #s = :s, updatedAt = :ts',
        ConditionExpression='#s = :open',
        ExpressionAttributeNames={'#s': 'status'},
        ExpressionAttributeValues={
            ':s':    InvoiceStatus.UNCOLLECTIBLE.value,
            ':ts':   now_iso,
            ':open': InvoiceStatus.OPEN.value,
        },
    )


def _mark_subscription_past_due(user_id: str, subscription_id: str, now_iso: str) -> None:
    subs_table.update_item(
        Key={'userId': user_id, 'subscriptionId': subscription_id},
        UpdateExpression='SET #s = :s, updatedAt = :ts',
        ExpressionAttributeNames={'#s': 'status'},
        ExpressionAttributeValues={
            ':s':  SubscriptionStatus.PAST_DUE.value,
            ':ts': now_iso,
        },
    )


def _provision_free_subscription(user_id: str, now_iso: str) -> str:
    """
    Creates a new ACTIVE FREE subscription for the user and persists it.
    Returns the new subscriptionId.
    """
    new_sub_id = f"sub_{uuid.uuid4().hex}"

    subs_table.put_item(Item={
        'userId':             user_id,
        'subscriptionId':     new_sub_id,
        'type':               SubscriptionType.FREE.value,
        'status':             SubscriptionStatus.ACTIVE.value,
        'createdAt':          now_iso,
        'updatedAt':          now_iso,
        'currentPeriodStart': now_iso,
        'currentPeriodEnd':   '',   # FREE subscriptions have no defined end
        'ttl':                ttl_three_years(),
    })

    return new_sub_id


def _update_user_active_subscription(user_id: str, new_sub_id: str, now_iso: str) -> None:
    """
    Updates the user's activeSubscriptionId.
    Resolves the Users table PK (email) via the USERS_USERID_GSI,
    then performs a targeted update_item.
    """
    # Resolve email (Users PK) from userId via the GSI
    gsi_response = users_table.query(
        IndexName='USERS_USERID_GSI',
        KeyConditionExpression=Key('userId').eq(user_id),
        Limit=1,
    )
    items = gsi_response.get('Items', [])
    if not items:
        raise ValueError(f"No user found for userId={user_id}")

    email = items[0]['email']

    users_table.update_item(
        Key={'email': email, 'userId': user_id},
        UpdateExpression='SET activeSubscriptionId = :sid, updatedAt = :ts',
        ExpressionAttributeValues={
            ':sid': new_sub_id,
            ':ts':  now_iso,
        },
    )

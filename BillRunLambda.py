import uuid
import boto3
from datetime import datetime, timezone
from decimal import Decimal

from boto3.dynamodb.conditions import Key, Attr

from model.subscription import SubscriptionType, SubscriptionStatus
from model.invoice import Invoice, InvoiceStatus

# ---------------------------------------------------------------------------
# DynamoDB resources
# ---------------------------------------------------------------------------

dynamodb = boto3.resource('dynamodb')
subscriptions_table = dynamodb.Table('Subscriptions')
invoices_table = dynamodb.Table('Invoices')

# ---------------------------------------------------------------------------
# Pricing table (monthly, in USD)
# ---------------------------------------------------------------------------

SUBSCRIPTION_PRICES: dict[SubscriptionType, Decimal] = {
    SubscriptionType.STANDARD: Decimal('9.99'),
    SubscriptionType.PRO:      Decimal('29.99'),
}

BILLING_CURRENCY = 'USD'

# ---------------------------------------------------------------------------
# Handler
# ---------------------------------------------------------------------------

def handler(event, context):
    """
    Bill run entry point.
    Generates an OPEN invoice for every user with an ACTIVE STANDARD or PRO
    subscription. Designed to be triggered on a monthly EventBridge schedule.
    """
    now_iso = datetime.now(timezone.utc).isoformat()

    subscriptions = _get_billable_subscriptions()
    print(f"[INFO] Found {len(subscriptions)} billable subscription(s).")

    created, errors = 0, 0

    for sub in subscriptions:
        try:
            invoice = _build_invoice(sub, now_iso)
            _save_invoice(invoice)
            created += 1
            print(f"[INFO] Invoice {invoice.invoice_id} created for "
                  f"userId={invoice.user_id} subscriptionId={invoice.subscription_id}.")
        except Exception as exc:
            errors += 1
            print(f"[ERROR] Failed to create invoice for "
                  f"userId={sub.get('userId')} "
                  f"subscriptionId={sub.get('subscriptionId')}: {exc}")

    print(f"[INFO] Bill run complete — created: {created}, errors: {errors}.")
    return {'created': created, 'errors': errors}

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_billable_subscriptions() -> list[dict]:
    """
    Returns all ACTIVE STANDARD or PRO subscriptions via a paginated query on
    the Subscriptions StatusIndex (ALL projection).
    """
    billable = []
    last_key = None

    while True:
        kwargs = {
            'IndexName': 'StatusIndex',
            'KeyConditionExpression': Key('status').eq(SubscriptionStatus.ACTIVE.value),
            'FilterExpression': Attr('type').is_in([
                SubscriptionType.STANDARD.value,
                SubscriptionType.PRO.value,
            ]),
        }
        if last_key:
            kwargs['ExclusiveStartKey'] = last_key

        response = subscriptions_table.query(**kwargs)
        billable.extend(response.get('Items', []))

        last_key = response.get('LastEvaluatedKey')
        if not last_key:
            break

    return billable


def _build_invoice(subscription: dict, now_iso: str) -> Invoice:
    """Creates an Invoice domain object from a raw subscription item."""
    sub_type = SubscriptionType(subscription['type'])
    amount   = SUBSCRIPTION_PRICES[sub_type]

    return Invoice(
        user_id         = subscription['userId'],
        invoice_id      = f"inv_{uuid.uuid4().hex}",
        subscription_id = subscription['subscriptionId'],
        amount          = amount,
        currency        = BILLING_CURRENCY,
        status          = InvoiceStatus.OPEN,
        period_start    = subscription['currentPeriodStart'],
        period_end      = subscription['currentPeriodEnd'],
        created_at      = now_iso,
        due_date        = subscription['currentPeriodEnd'],
    )


def _save_invoice(invoice: Invoice) -> None:
    """Persists an Invoice to DynamoDB."""
    invoices_table.put_item(Item=invoice.to_item())

from ninja import Schema
from decimal import Decimal


class TransactionSchema(Schema):
    amount: Decimal
    payer_id: int
    wallet_id: str

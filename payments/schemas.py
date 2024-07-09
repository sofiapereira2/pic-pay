from ninja import ModelSchema, Schema

from payments.models import Transactions


class TransactionSchema(ModelSchema):
    class Meta:
        model = Transactions
        exclude = ['id', 'date']

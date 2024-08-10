from ninja import Router
from .models import Transactions
from users.models import User
from .schemas import TransactionSchema
from django.shortcuts import get_object_or_404
from rolepermissions.checkers import has_permission
from django.db import transaction as django_transaction
import requests
from django.conf import settings
from django_q.tasks import async_task
from .tasks import send_notification
from core.auth import JWTAuth

payments_router = Router()


@payments_router.post('/',
                      response={200: dict,
                                400: dict,
                                403: dict},
                      auth=JWTAuth())
def transaction(request, transaction: TransactionSchema):
    print(transaction)
    payer = get_object_or_404(User, id=transaction.payer_id)
    payee = get_object_or_404(User, wallet_id=transaction.wallet_id)

    if payer.amount < transaction.amount:
        return 400, {'error': 'Insufficient balance'}

    if not has_permission(payer, 'make_transfer'):
        return 403, {'error': 'You do not have permission to perform'
                     'transfers'}

    if not has_permission(payee, 'receive_transfer'):
        return 403, {'error': 'This user cannot receive transfers'}

    with django_transaction.atomic():
        payer.pay(transaction.amount)
        payee.receive(transaction.amount)

        transact = Transactions(
            amount=transaction.amount,
            payer_id=transaction.payer_id,
            payee_id=payee.id,
        )
        payer.save()
        payee.save()
        transact.save()

        response = requests.get(settings.AUTHORIZE_TRANSFER_ENDPOINT).json()
        if response.get('status') != 'authorized':
            raise Exception()

    async_task(send_notification, payer.first_name, payee.first_name,
               transaction.amount)

    return 200, {'transaction_id': 1}

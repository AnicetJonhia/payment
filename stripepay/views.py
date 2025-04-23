import stripe
import json
from django.conf import settings
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Order
import logging
logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

class CreateCheckoutSessionView(APIView):
    def post(self, request):
        product_name = "Produit test"
        amount = 2000  # en centimes, ex: 20.00 €

        order = Order.objects.create(
            product_name=product_name,
            amount=amount
        )

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': product_name},
                    'unit_amount': amount,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://localhost:8000/success/',
            cancel_url='http://localhost:8000/cancel/',
            metadata={'order_id': str(order.id)},
        )

        order.stripe_checkout_session_id = session.id
        order.save()

        return Response({'id': session.id})


@csrf_exempt
def stripe_webhook(request):

    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')


    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_id = session['metadata'].get('order_id')

        try:
            order = Order.objects.get(id=order_id)
            order.paid = True
            order.save()
            logger.info(f"✅ Commande {order.id} marquée comme payée.")
        except Order.DoesNotExist:
            logger.error(f"❌ Order avec ID {order_id} introuvable.")

    return HttpResponse(status=200)

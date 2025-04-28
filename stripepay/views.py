import stripe
import json
from django.conf import settings
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import PaymentIntentRequestSerializer
from .models import Order
import logging
logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

class CreateCheckoutSessionView(APIView):
    """Créer une session Stripe dynamiquement à partir du frontend"""
    def post(self, request):
        data = request.data

        # On récupère les informations envoyées par le frontend
        product_name = data.get('product_name')
        amount = data.get('amount')  # en centimes
        quantity = data.get('quantity', 1)

        if not product_name or not amount:
            return Response({"error": "product_name et amount sont requis."}, status=400)

        # On crée une commande
        order = Order.objects.create(
            product_name=product_name,
            amount=amount,
            quantity=quantity,
        )

        # On crée la session Stripe
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': product_name},
                    'unit_amount': amount,
                },
                'quantity': quantity,
            }],
            mode='payment',
            success_url='http://localhost:8000/api/payment/success/',
            cancel_url='http://localhost:8000/api/payment/cancel/',
            metadata={'order_id': str(order.id)},
        )

        # On stocke la session_id Stripe
        order.stripe_checkout_session_id = session.id
        order.save()

        return Response({
            'id': session.id,
            'url': session.url
        })

class CreatePaymentIntentView(APIView):
    """Créer un PaymentIntent pour Stripe Elements"""
    def post(self, request):
        # Valider les données de la requête avec le serializer
        serializer = PaymentIntentRequestSerializer(data=request.data)
        if serializer.is_valid():
            product_name = serializer.validated_data['product_name']
            amount = serializer.validated_data['amount']
            quantity = serializer.validated_data['quantity']

            # Créer la commande dans la base de données
            order = Order.objects.create(
                product_name=product_name,
                amount=amount,
                quantity=quantity,
            )

            try:
                # Créer un PaymentIntent avec Stripe
                intent = stripe.PaymentIntent.create(
                    amount=amount * quantity,
                    currency='usd',
                    metadata={'order_id': str(order.id)},
                )

                # Stocker le PaymentIntent ID pour vérification future
                order.stripe_checkout_session_id = intent.id
                order.save()

                # Retourner le clientSecret à l'utilisateur
                return Response({
                    'clientSecret': intent.client_secret,
                    'order_id': order.id,
                })

            except stripe.error.StripeError as e:
                # Gérer les erreurs Stripe
                return Response({"error": "Erreur Stripe: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


class PaymentSuccessView(APIView):
    """API appelée après un paiement réussi"""
    def get(self, request):
        return Response({"message": "Paiement réussi !"})


class PaymentCancelView(APIView):
    """API appelée après un paiement annulé"""
    def get(self, request):
        return Response({"message": "Paiement annulé."})


class RefundOrderView(APIView):
    """API pour rembourser une commande"""
    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            if not order.paid:
                return Response({"error": "Commande non payée, pas de remboursement possible."}, status=400)

            refund = stripe.Refund.create(
                payment_intent=order.stripe_checkout_session_id
            )

            order.refunded = True
            order.save()
            logger.info(f"🔄 Remboursement de la commande {order.id} effectué.")
            return Response({"message": "Commande remboursée.", "refund": refund})
        except Order.DoesNotExist:
            return Response({"error": "Commande introuvable."}, status=404)
        except stripe.error.StripeError as e:
            logger.error(f"Erreur de remboursement Stripe: {str(e)}")
            return Response({"error": "Erreur Stripe."}, status=500)

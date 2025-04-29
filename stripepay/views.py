

import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order
from .serializers import PaymentIntentRequestSerializer, StripeSessionResponseSerializer



stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

class CreateCheckoutSessionView(APIView):
    def post(self, request):
        serializer = PaymentIntentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        product_name = validated_data['product_name']
        amount = validated_data['amount']
        quantity = validated_data['quantity']

        order = Order.objects.create(
            product_name=product_name,
            amount=amount,
            quantity=quantity,
        )

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

        order.stripe_checkout_session_id = session.id
        order.save()

        response_serializer = StripeSessionResponseSerializer({
            'id': session.id,
            'url': session.url,
        })

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

class CreatePaymentIntentView(APIView):
    """Créer un PaymentIntent pour Stripe Elements"""
    def post(self, request):

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
            print(f"✅ Commande {order.id} marquée comme payée.")
        except Order.DoesNotExist:
            print(f"❌ Order avec ID {order_id} introuvable.")

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

            return Response({"message": "Commande remboursée.", "refund": refund})
        except Order.DoesNotExist:
            return Response({"error": "Commande introuvable."}, status=404)
        except stripe.error.StripeError as e:

            return Response({"error": "Erreur Stripe."}, status=500)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .paypal_client import client
from paypalcheckoutsdk.orders import OrdersCreateRequest, OrdersCaptureRequest
from .models import Order
from .serializers import PayPalOrderRequestSerializer, OrderSerializer

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json



class PayPalCreateOrderView(APIView):
    """Créer une commande PayPal et l'enregistrer localement"""
    def post(self, request):
        # Valider les données entrantes
        serializer = PayPalOrderRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Créer l'objet Order en base
        order = Order.objects.create(
            product_name=data['product_name'],
            amount=data['amount'],
            quantity=data['quantity'],
            currency=data.get('currency', 'USD'),
        )

        # Préparer la requête PayPal
        total = (order.amount * order.quantity) / 100
        request_body = {
            "intent": "CAPTURE",
            "purchase_units": [{
                "amount": {
                    "currency_code": order.currency,
                    "value": f"{total:.2f}"
                },
                "description": order.product_name,
            }],
            "application_context": {
                "return_url": f"http://localhost:8000/api/paypal/success/?token={order.paypal_order_id}",
                "cancel_url": f"http://localhost:8000/api/paypal/cancel/?token={order.paypal_order_id}"
            }
        }

        paypal_request = OrdersCreateRequest()
        paypal_request.prefer("return=representation")
        paypal_request.request_body(request_body)

        try:
            response = client.execute(paypal_request)
            paypal_id = response.result.id

            # Mettre à jour l'Order local
            order.paypal_order_id = paypal_id
            order.save()

            out_serializer = OrderSerializer(order)
            return Response({
                'order': out_serializer.data,
                'paypal': response.result.__dict__['_dict']
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            order.status = 'failed'
            order.save()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PayPalCaptureOrderView(APIView):
    """Capturer un paiement PayPal et mettre à jour la commande"""
    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order non trouvée."}, status=status.HTTP_404_NOT_FOUND)

        if not order.paypal_order_id:
            return Response({"error": "Aucun order_id PayPal associé."}, status=status.HTTP_400_BAD_REQUEST)

        capture_request = OrdersCaptureRequest(order.paypal_order_id)
        capture_request.prefer("return=representation")

        try:
            response = client.execute(capture_request)

            # Mettre à jour l'état de la commande
            order.status = 'paid'
            order.paid = True
            order.save()

            out_serializer = OrderSerializer(order)
            return Response({
                'order': out_serializer.data,
                'capture': response.result.__dict__['_dict']
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@csrf_exempt
def paypal_webhook(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

    try:
        if request.body:
            try:
                event = json.loads(request.body.decode('utf-8'))
            except json.JSONDecodeError:
                return JsonResponse({'error': 'JSON invalide'}, status=400)
        else:
            return JsonResponse({'error': 'Corps vide'}, status=400)

        print("Webhook reçu :", event)

        event_type = event.get("event_type")
        resource = event.get("resource", {})
        paypal_order_id = resource.get("id")

        print("Type d'événement :", event_type)
        print("Paypal Order ID :", paypal_order_id)

        if event_type == "PAYMENT.CAPTURE.COMPLETED":
            try:
                order = Order.objects.get(paypal_order_id=paypal_order_id)
                order.status = "completed"
                order.paid = True
                order.save()
                print("Commande mise à jour :", order.id)
            except Order.DoesNotExist:
                print("Commande non trouvée.")

        return JsonResponse({'status': 'ok'})

    except Exception as e:
        print("Erreur webhook :", str(e))
        return JsonResponse({'error': str(e)}, status=500)




class PayPalSuccessView(APIView):
    """Gérer le succès de la commande PayPal"""
    def get(self, request):
        # Récupérer le token PayPal (order_id) dans l'URL
        token = request.GET.get('token')

        if not token:
            return Response({"error": "Token manquant."}, status=status.HTTP_400_BAD_REQUEST)

        # Vérifier si la commande existe
        try:
            order = Order.objects.get(paypal_order_id=token)
        except Order.DoesNotExist:
            return Response({"error": "Commande non trouvée."}, status=status.HTTP_404_NOT_FOUND)

        # Capturer le paiement de la commande PayPal
        capture_request = OrdersCaptureRequest(order.paypal_order_id)
        capture_request.prefer("return=representation")

        try:
            response = client.execute(capture_request)

            # Mettre à jour l'état de la commande
            order.status = 'paid'
            order.paid = True
            order.save()

            # Sérialiser et renvoyer la commande mise à jour
            out_serializer = OrderSerializer(order)
            return Response({
                'order': out_serializer.data,
                'capture': response.result.__dict__['_dict']
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class PayPalCancelView(APIView):
    """Gérer l'annulation de la commande PayPal"""
    def get(self, request):
        # Optionnel : log ou afficher un message personnalisé
        return Response({"message": "Votre paiement a été annulé."}, status=status.HTTP_200_OK)

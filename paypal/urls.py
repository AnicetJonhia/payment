from django.urls import path

from .views import PayPalCreateOrderView, PayPalCaptureOrderView, paypal_webhook, PayPalSuccessView, PayPalCancelView


urlpatterns = [
    path('create-order/', PayPalCreateOrderView.as_view(), name='paypal-create-order'),
    path('capture-order/<int:order_id>/', PayPalCaptureOrderView.as_view(), name='paypal-capture-order'),
    path('webhook/', paypal_webhook, name='paypal-webhook'),
    path('success/',PayPalSuccessView.as_view(), name='paypal-success'),
    path('cancel/', PayPalCancelView.as_view(), name='paypal-cancel'),
]
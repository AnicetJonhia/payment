from django.urls import path
from .views import PayPalCreateOrderView, PayPalCaptureOrderView


urlpatterns = [
    path('create-order/', PayPalCreateOrderView.as_view(), name='paypal-create-order'),
    path('capture-order/<int:order_id>/', PayPalCaptureOrderView.as_view(), name='paypal-capture-order'),
]
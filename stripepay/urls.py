from django.urls import path
from .views import (
    CreateCheckoutSessionView,
    CreatePaymentIntentView ,
    stripe_webhook,
    PaymentSuccessView,
    PaymentCancelView,
    RefundOrderView
)

urlpatterns = [
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('create-payment-intent/', CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    path('webhook/', stripe_webhook, name='stripe-webhook'),
    path('success/', PaymentSuccessView.as_view(), name='payment-success'),
    path('cancel/', PaymentCancelView.as_view(), name='payment-cancel'),
    path('refund/<int:order_id>/', RefundOrderView.as_view(), name='payment-refund'),

]

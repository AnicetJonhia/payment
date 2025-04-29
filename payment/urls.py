from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/stripepay/', include('stripepay.urls')),
    path('api/paypal/', include('paypal.urls')),
]

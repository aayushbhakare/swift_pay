from django.contrib import admin
from django.urls import path, include
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({"status": "healthy", "service": "swiftpay-api", "version": "1.0.0"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/health/', health_check, name='health_check'),
    path('api/v1/payments/', include('swiftpay.payments.urls')),
    path('api/v1/merchants/', include('swiftpay.merchants.urls')),
    path('api/v1/auth/', include('swiftpay.authentication.urls')),
]

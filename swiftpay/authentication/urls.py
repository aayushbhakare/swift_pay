from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from swiftpay.authentication import views

urlpatterns = [
    path('config/', views.get_auth_config, name='auth_config'),
    path('register/', views.register_view, name='register'),
    path('login/', views.CustomTokenObtainPairView.as_view(), name='login'),
    path('google/', views.google_login, name='google_login'),
    path('otp/send/', views.send_otp, name='send_otp'),
    path('otp/verify/', views.verify_phone_otp, name='verify_otp'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

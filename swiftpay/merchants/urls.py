from django.urls import path
from . import views

urlpatterns = [
    path('balance/', views.get_merchant_balance, name='merchant_balance'),
    path('profile/', views.MerchantProfileView.as_view(), name='update_profile'),
    path('api-key/generate/', views.generate_api_key, name='generate_api_key'),
]

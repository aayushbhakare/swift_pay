from django.urls import path

from apps.merchants.views import get_merchant_balance



urlpatterns = [

    path('balance/', get_merchant_balance, name='merchant_balance'),

]


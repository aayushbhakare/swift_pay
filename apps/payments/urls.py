from django.urls import path

from apps.payments.views import create_payment, capture_payment, get_payment



urlpatterns = [

    path('', create_payment, name='create_payment'),

    path('<uuid:payment_id>/', get_payment, name='get_payment'),

    path('<uuid:payment_id>/capture/', capture_payment, name='capture_payment'),

]


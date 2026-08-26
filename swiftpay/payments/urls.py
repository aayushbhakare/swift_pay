from django.urls import path
from swiftpay.payments.views import PaymentListCreateAPIView, capture_payment, get_payment
from swiftpay.payments.checkout_views import get_checkout_payment, process_checkout_payment

urlpatterns = [
    path('', PaymentListCreateAPIView.as_view(), name='payment_list_create'),
    path('<uuid:payment_id>/', get_payment, name='get_payment'),
    path('<uuid:payment_id>/capture/', capture_payment, name='capture_payment'),
    
    # Public Checkout APIs
    path('checkout/<uuid:payment_id>/', get_checkout_payment, name='get_checkout_payment'),
    path('checkout/<uuid:payment_id>/process/', process_checkout_payment, name='process_checkout_payment'),
]

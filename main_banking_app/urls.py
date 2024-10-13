# banking_app/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView, AccountCreateView, AccountDetailView,
    DepositView, WithdrawView, TransferView, TransactionHistoryView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('accounts/create/', AccountCreateView.as_view(), name='account_create'),
    path('accounts/detail/', AccountDetailView.as_view(), name='account_detail'),
    path('accounts/deposit/', DepositView.as_view(), name='deposit'),
    path('accounts/withdraw/', WithdrawView.as_view(), name='withdraw'),
    path('transfer/', TransferView.as_view(), name='transfer'),
    path('transactions/', TransactionHistoryView.as_view(), name='transaction_history'),
]
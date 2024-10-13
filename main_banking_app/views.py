# banking_app/views.py
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Account, Transaction
from .serializers import UserSerializer, AccountSerializer, TransactionSerializer, TransferSerializer
from decimal import Decimal

class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer

class AccountCreateView(generics.CreateAPIView):
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AccountDetailView(APIView):
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        account_details = Account.objects.filter(user=request.user)
        return Response(data={"user": account_details[0].user.username, "account_detaisl": [ {"account_name": details.name, "account_balance": details.balance} for details in account_details]}, status=status.HTTP_200_OK)

class DepositView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        account = get_object_or_404(Account, user=request.user)
        amount = Decimal(request.data.get('amount', 0))
        
        if amount <= 0:
            return Response({"error": "Invalid deposit amount"}, status=status.HTTP_400_BAD_REQUEST)

        account.balance += amount
        account.save()

        transaction = Transaction.objects.create(
            account=account,
            amount=amount,
            transaction_type='deposit'
        )

        return Response({
            "message": "Deposit successful",
            "new_balance": account.balance,
            "transaction": TransactionSerializer(transaction).data
        })

class WithdrawView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        account = get_object_or_404(Account, user=request.user)
        amount = Decimal(request.data.get('amount', 0))
        
        if amount <= 0:
            return Response({"error": "Invalid withdrawal amount"}, status=status.HTTP_400_BAD_REQUEST)

        if account.balance < amount:
            return Response({"error": "Insufficient funds"}, status=status.HTTP_400_BAD_REQUEST)

        account.balance -= amount
        account.save()

        transaction = Transaction.objects.create(
            account=account,
            amount=-amount,
            transaction_type='withdrawal'
        )

        return Response({
            "message": "Withdrawal successful",
            "new_balance": account.balance,
            "transaction": TransactionSerializer(transaction).data
        })

class TransferView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransferSerializer

    @transaction.atomic
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        from_account = get_object_or_404(Account, name=serializer.validated_data['from_account'], user=request.user)
        to_account = get_object_or_404(Account, name=serializer.validated_data['to_account'])
        amount = serializer.validated_data['amount']

        if from_account.balance < amount:
            return Response({"error": "Insufficient funds"}, status=status.HTTP_400_BAD_REQUEST)

        from_account.balance -= amount
        to_account.balance += amount

        from_account.save()
        to_account.save()

        Transaction.objects.create(account=from_account, amount=-amount, transaction_type='transfer_out')
        Transaction.objects.create(account=to_account, amount=amount, transaction_type='transfer_in')

        return Response({"message": "Transfer successful"})

class TransactionHistoryView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(account__user=self.request.user).order_by('-timestamp')
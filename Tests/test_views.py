import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from decimal import Decimal
from main_banking_app.models import Account, Transaction
from main_banking_app.serializers import TransactionSerializer
from django.contrib.auth.models import User
from unittest.mock import patch

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user(db):
    def _create_user(username, password):
        user = User.objects.create_user(username=username, password=password)
        return user
    return _create_user

@pytest.fixture
def create_account(db):
    def _create_account(user, balance=Decimal('1000.00')):
        account = Account.objects.create(user=user, name=f"{user.username}_account", balance=balance)
        return account
    return _create_account

@pytest.fixture
def create_transaction(db):
    def _create_transaction(account, amount, transaction_type):
        transaction = Transaction.objects.create(account=account, amount=amount, transaction_type=transaction_type)
        return transaction
    return _create_transaction


### **Tests for the RegisterView**

def test_register_view(api_client, db):
    url = reverse('register')
    data = {"username": "testuser", "password": "password123"}
    
    response = api_client.post(url, data)
    
    assert response.status_code == 201  # Created
    assert User.objects.filter(username='testuser').exists()


### **Tests for the AccountCreateView**

@pytest.mark.django_db
def test_create_account_view(api_client, create_user):
    user = create_user("testuser", "password123")
    api_client.force_authenticate(user=user)
    url = reverse('account_create')
    
    data = {"name": "savings_account"}
    response = api_client.post(url, data)
    
    assert response.status_code == 201  # Created
    assert Account.objects.filter(user=user, name="savings_account").exists()


### **Tests for the AccountDetailView**

@pytest.mark.django_db
def test_account_detail_view(api_client, create_user, create_account):
    user = create_user("testuser", "password123")
    create_account(user)
    
    api_client.force_authenticate(user=user)
    url = reverse('account_detail')

    response = api_client.get(url)
    
    assert response.status_code == 200  # OK
    assert 'account_detaisl' in response.data
    assert len(response.data['account_detaisl']) == 1


### **Tests for the DepositView**

@pytest.mark.django_db
def test_deposit_view(api_client, create_user, create_account):
    user = create_user("testuser", "password123")
    account = create_account(user)
    
    api_client.force_authenticate(user=user)
    url = reverse('deposit')
    
    data = {"amount": "200.00"}
    response = api_client.post(url, data)

    account.refresh_from_db()  # Refresh to see updated balance
    
    assert response.status_code == 200  # OK
    assert account.balance == Decimal("1200.00")  # Increased balance
    assert Transaction.objects.filter(account=account, amount=200, transaction_type="deposit").exists()


@pytest.mark.django_db
def test_deposit_invalid_amount(api_client, create_user, create_account):
    user = create_user("testuser", "password123")
    account = create_account(user)
    
    api_client.force_authenticate(user=user)
    url = reverse('deposit')
    
    data = {"amount": "-50.00"}  # Invalid amount
    response = api_client.post(url, data)
    
    assert response.status_code == 400  # Bad Request
    assert "Invalid deposit amount" in response.data['error']


### **Tests for the WithdrawView**

@pytest.mark.django_db
def test_withdraw_view(api_client, create_user, create_account):
    user = create_user("testuser", "password123")
    account = create_account(user)
    
    api_client.force_authenticate(user=user)
    url = reverse('withdraw')
    
    data = {"amount": "200.00"}
    response = api_client.post(url, data)

    account.refresh_from_db()
    
    assert response.status_code == 200  # OK
    assert account.balance == Decimal("800.00")  # Decreased balance
    assert Transaction.objects.filter(account=account, amount=-200, transaction_type="withdrawal").exists()


@pytest.mark.django_db
def test_withdraw_insufficient_funds(api_client, create_user, create_account):
    user = create_user("testuser", "password123")
    account = create_account(user)
    
    api_client.force_authenticate(user=user)
    url = reverse('withdraw')
    
    data = {"amount": "2000.00"}  # More than balance
    response = api_client.post(url, data)
    
    assert response.status_code == 400  # Bad Request
    assert "Insufficient funds" in response.data['error']


### **Tests for the TransferView**

@pytest.mark.django_db
def test_transfer_view(api_client, create_user, create_account):
    user = create_user("testuser", "password123")
    from_account = create_account(user, balance=Decimal('1000.00'))
    to_account = create_account(create_user("otheruser", "password123"), balance=Decimal('500.00'))
    
    api_client.force_authenticate(user=user)
    url = reverse('transfer')
    
    data = {"from_account": from_account.name, "to_account": to_account.name, "amount": "100.00"}
    response = api_client.post(url, data)

    from_account.refresh_from_db()
    to_account.refresh_from_db()
    
    assert response.status_code == 200  # OK
    assert from_account.balance == Decimal("900.00")
    assert to_account.balance == Decimal("600.00")


@pytest.mark.django_db
def test_transfer_insufficient_funds(api_client, create_user, create_account):
    user = create_user("testuser", "password123")
    from_account = create_account(user, balance=Decimal('50.00'))
    to_account = create_account(create_user("otheruser", "password123"), balance=Decimal('500.00'))
    
    api_client.force_authenticate(user=user)
    url = reverse('transfer')
    
    data = {"from_account": from_account.name, "to_account": to_account.name, "amount": "100.00"}
    response = api_client.post(url, data)
    
    assert response.status_code == 400  # Bad Request
    assert "Insufficient funds" in response.data['error']


### **Tests for TransactionHistoryView**

@pytest.mark.django_db
def test_transaction_history_view(api_client, create_user, create_account, create_transaction):
    user = create_user("testuser", "password123")
    account = create_account(user)
    create_transaction(account, amount=200, transaction_type='deposit')
    create_transaction(account, amount=-50, transaction_type='withdrawal')
    
    api_client.force_authenticate(user=user)
    url = reverse('transaction_history')

    response = api_client.get(url)

    assert response.status_code == 200  # OK
    assert len(response.data) == 2
    assert response.data[0]['transaction_type'] == 'withdrawal'
    assert response.data[1]['transaction_type'] == 'deposit'

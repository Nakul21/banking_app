# Banking App

This is a Django-based banking application that provides API endpoints for user registration, account creation, deposits, withdrawals, transfers, and transaction history. The app uses Django REST Framework and JWT for authentication.

## Features

- User Registration
- Account Creation
- Deposit, Withdrawal, and Transfer Money
- Transaction History

## Prerequisites

Ensure you have the following installed before proceeding:

- Python 3.9 or higher
- Docker & Docker Compose
- Git

---

## Getting Started - Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/banking-app.git
cd banking-app
```

### 2 . setup the virtual env

```bash

python -m venv banking_app_venv
source banking_app_venv/bin/activate  # For Linux/macOS
# or
banking_app_venv\Scripts\activate  # For Windows
```
### 3 install dependencies

```bash
pip install -r requirements.txt
```
### 4. Run the migrations

```bash
python manage.py makemigrations
python manage.py migrate
```
### 5. runserver

```bash
python manage.py runserver
```

### Running with Docker
You can also run the app using Docker.

### 1. Build the Docker container
```bash

docker-compose build
```

### 2. Run the containers
```bash

docker-compose up
```
#### This command will run the Django app in a container and expose it at http://127.0.0.1:8000/.

### 3. Running migrations inside the container
##### Open a new terminal window and run the following command:

```bash

docker-compose exec web python manage.py migrate
```
#### This will run the database migrations inside the Docker container.

### 4. Create a superuser (optional)
#### To create a superuser, run the following command:

```bash

docker-compose exec web python manage.py createsuperuser
```

### 5. Stopping the containers
#### To stop the running containers, press Ctrl + C in the terminal where docker-compose up is running or use the following command:

```bash

docker-compose down
```

### Running Tests
#### To run the tests locally using pytest, make sure your virtual environment is active and use the following command:

```bash

pytest
```
#### To run tests inside the Docker container:

```bash

docker-compose exec web pytest
```
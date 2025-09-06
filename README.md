# qr-payment-server

## About

This is 2nd microservice of project which contain 3 components:

1) TG-bot which connects via API with backend server and show QR-code for payment and access token if payment valid

2) Python-backend server which is able to validate transaction, generate qr-codes and generate tokens

3) Test-net based on ETH(or any else) by which we can provide transactions

## Initialization local machine

```bash
python -m app.db.init_db # Creates db and tables in postgresql
```

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload # Creates ASGI-server. Ready to client interaction
```

## Initialization docker

```bash
docker network create qrb-network # creates external docker-network
```

```bash
docker-compose up --build
```

# wealthy-option
Wealth option trading strategy implemented in python using ibkr

## Run locally

1. Run `source setup-dev.sh` 
2. Start IB Gateway program
3. Run `main.py`

## Run locally with docker-compose

1. Ensure any changes to requirements have been pushed to their main brach in git
2. `docker-compose up`


Create group
```
az acr create --resource-group trading-bots --name wealthoption --sku Basic
```

Build images
...

Tag images
```
docker tag ghcr.io/gnzsnz/ib-gateway:stable wealthyoption.azurecr.io/ib-gateway:latest
docker tag algo-trader-wealthy-option-bot wealthyoption.azurecr.io/wealthy-option:latest
```

Push images
```
docker push wealthyoption.azurecr.io/ib-gateway:latest
docker push wealthyoption.azurecr.io/wealthy-option:latest
```

```
az container create --resource-group trading-bots --file docker-compose.yml --name algo-trader 
```
# wealthy-option
Wealth option trading strategy implemented in python using ibkr

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
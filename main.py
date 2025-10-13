import asyncio
import os

from ib_async import *
from ibkrkit.ibkr_utils import wait_for_ibkr_ready
from wealthy_option import WealthyOption


HOST = "ib-gateway"     # use the gateway docker service
PORT = 4004             # paper trading


async def main():    
    ready = await wait_for_ibkr_ready(HOST, PORT)
    if not ready:
        raise RuntimeError("IB Gateway service is not ready - exiting.")
    
    print("Starting docker_main.py")
    
    account_id = os.environ["ACCOUNT_ID"]
    client_id = os.environ["CLIENT_ID"]
    
    strategy = WealthyOption()
    strategy.run(host=HOST, port=PORT, client_id=client_id, account_id=account_id)


if __name__ == "__main__":
    asyncio.run(main())

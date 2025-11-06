import asyncio
import os

from ib_async import *
from datetime import datetime

from ibkrkit.ibkr_utils import wait_for_ibkr_ready
from wealthy_option import WealthyOption


async def main():    
    host = os.environ["HOST"]
    port = os.environ["PORT"]
    client_id = os.environ["CLIENT_ID"]
    account_id = os.environ["ACCOUNT_ID"]
    
    ready = await wait_for_ibkr_ready(host, port)
    if not ready:
        raise RuntimeError("IB Gateway service is not ready - exiting.")
    print("Starting docker_main.py!!!")
    
    # Setup IBKR API logging 
    util.logToFile(f"./log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt")
    
    strategy = WealthyOption()
    strategy.run(host=host, port=port, client_id=client_id, account_id=account_id)


if __name__ == "__main__":
    asyncio.run(main())

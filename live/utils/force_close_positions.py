from ib_async import IB, util
from ib_async.order import MarketOrder
import logging

def close_all_positions():
    ib = IB()
    ib.connect('127.0.0.1', 7496, clientId=1)

    positions = ib.positions()
    if not positions:
        print("No open positions found.")
        ib.disconnect()
        return

    print(f"Found {len(positions)} open positions.\n")

    for pos in positions:
        contract = pos.contract
        position = pos.position

        print(f"Closing {position} of {contract.symbol} ({contract.secType})")

        # Determine opposite side to flatten the position
        if position > 0:
            order = MarketOrder('SELL', abs(position))
        elif position < 0:
            order = MarketOrder('BUY', abs(position))
        else:
            continue

        trade = ib.placeOrder(contract, order)
        ib.sleep(1)  # give it a moment to register
        print(f"Order placed: {order.action} {abs(position)} {contract.symbol}")

    print("All positions closed (orders sent).")
    ib.disconnect()

if __name__ == "__main__":
    close_all_positions()

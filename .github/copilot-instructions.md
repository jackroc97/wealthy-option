## Purpose

Quick, actionable guidance for AI coding agents working on the `wealthy-option` repository.
Focus on what to change, where to look, and how to run common developer workflows.

## Big picture

- This repo implements a single trading strategy (WealthyOption) in Python under `bot/` that drives interaction with Interactive Brokers via the `ib_async` and `ibkrkit` libraries.
- Architecture:
  - `bot/` — main strategy code and entrypoint (`bot/main.py`, `bot/wealthy_option.py`). Strategy classes inherit from `IbkrStrategy` and implement lifecycle hooks like `on_start`, `tick`, and `on_stop`.
  - `analysis/` — small utilities for post-run or reporting (e.g. `analysis/get_bot_trades.py`).
  - `backtests/` — placeholder for backtest code (inspect when present).
  - Top-level Docker artifacts (`dockerfile`, `docker-compose.yml`) define the container runtime and an `ib-gateway` service used for paper trading.

## How to run locally (discovered from repo)

- Dev setup (non-docker):
  1. Run `source setup-dev.sh` (README).
  2. Start IB Gateway (external program) and ensure it accepts API connections.
  3. Run `python bot/main.py`.

- With Docker Compose (quick):
  - `docker-compose up` (README + `docker-compose.yml`).
  - Important env vars exposed in `docker-compose.yml`: `HOST` (set to `ib-gateway` in compose), `PORT` (4004 for paper), `ACCOUNT_ID`, `CLIENT_ID`. In containers, `main.py` expects `HOST`, `PORT`, `CLIENT_ID`, `ACCOUNT_ID`.
  - The image built by `dockerfile` runs `python -u main.py` in `/app`.

## Key runtime / integration points

- IBKR integration: uses `ib_async` and helpers from `ibkrkit` (look at imports in `bot/main.py` and `bot/wealthy_option.py`). Expect asynchronous patterns and data streams (`IbkrDataStream`, `IbkrOptionChain`).
- Strategy contract definitions: the strategy hardcodes an `ES` futures contract and uses `FuturesOption` to create option legs (see `wealthy_option.WealthyOption` class). When modifying strikes / expirations follow the patterns in `select_short_put` / `select_long_put`.
- Order placement/logging: `place_bracket_order`, `logger.log_order`, and `logger.log_fill` are used to record trades; preserve calls to these when changing order logic so existing logging remains consistent.

## Project-specific conventions and patterns

- Strategy lifecycle: subclass `IbkrStrategy` and implement `async def on_start(self)`, `async def tick(self)`, and `async def on_stop(self)`. `tick()` runs periodically — prefer async calls and `self.ib` helpers for data and orders.
- Use of synchronous-looking calls: `bot/main.py` runs an asyncio `main()` then calls `strategy.run(...)` (the strategy run method is expected to start its own loop). Avoid changing that call without verifying how `IbkrStrategy.run` is implemented in `ibkrkit`.
- Time and selection logic: `WealthyOption` uses `self.now`, `self.now.weekday()`, and datetime arithmetic to adjust DTEs. When adding features, mirror the time-window checks in `should_open_new_position()`.
- Prices are rounded to the nearest quarter via `round_to_nearest_quarter`; preserve this helper when calculating take-profit/stop-loss levels.

## Dependencies and external repos

- `requirements.txt` contains pinned versions and two editable Git dependencies:
  - `git+https://github.com/jackroc97/btkit.git@main#egg=btkit`
  - `git+https://github.com/jackroc97/ibkit.git@main#egg=ibkrkit`
- Expect changes to these libraries to affect behavior; run `pip install -r requirements.txt` after edits to dependency pins.

## Notable files to inspect when editing behavior

- `bot/wealthy_option.py` — main strategy logic; examples of contract creation, option-chain lookup, and bracket order placement.
- `bot/main.py` — entrypoint; sets env vars and waits for IB Gateway readiness (`wait_for_ibkr_ready`).
- `docker-compose.yml` & `dockerfile` — containerized runtime and required environment variables/ports for IB gateway integration.
- `analysis/get_bot_trades.py` — demonstrates usage of `FlexReport` to fetch historical trades (contains `TOKEN` and `QUERY_ID` used for reports). Use as example for reporting scripts.
- `requirements.txt` — pinned libraries and editable git deps; changing these requires rebuilding containers.

## Safety and secrets

- `analysis/get_bot_trades.py` currently contains a numeric `TOKEN` and `QUERY_ID`. Treat these as sensitive: do NOT hardcode credentials in production branches. If you modify reporting scripts, prefer environment variables or a local secrets file excluded via `.gitignore`.

## When creating changes, examples and small rules

- If adding options logic, follow existing pattern:
  - qualify contracts with `await self.ib.qualifyContractsAsync(contract)`
  - create data streams with `await IbkrDataStream.create(self.ib, contract)`
  - compute limit/tp/sl from data streams as in `tick()` (see code for `limit_price`, `take_profit_price`, `stop_loss_price`).
- When changing Docker behavior, update both `dockerfile` and `docker-compose.yml` and note that images are tagged/pushed manually (README shows `docker tag` and `docker push` steps).

## What not to change without verification

- Don't change the hardcoded ports in `docker-compose.yml` or `dockerfile` without testing local IB Gateway connectivity.
- Avoid switching async flow in `bot/main.py` (the ready wait and subsequent `strategy.run` handshake are important).

## Quick checklist for PR reviewers (agents)

- Run `source setup-dev.sh` and `python bot/main.py` locally (or `docker-compose up`) to smoke-test.
- Check `requirements.txt` for editable git deps before changing behavior that depends on `ibkrkit` or `btkit`.
- If you touch `analysis/get_bot_trades.py`, move tokens to env vars and add a note to README.

---

If anything here is incomplete or confusing, tell me which area (runtime, strategy, reporting, or docker) and I'll expand the guidance with examples or tests.

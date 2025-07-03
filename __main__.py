import asyncio
from decimal import Decimal
from infrastructure import TronWrapper
from app import (
    TronAddress,
    PASSPHRASE,
    PROVIDER_URL, 
    NETWORK, 
    USDT_CONTRACT_ADDRESS
)

DECIMALS = 10**6

async def main():
    tron_wrapper = TronWrapper(provider_url=PROVIDER_URL, network=NETWORK)
    passphrase = PASSPHRASE
    tron_addr = TronAddress(passphrase=passphrase, tron_wrapper=tron_wrapper)

    while True:
        try:
            print(f"Your address: {tron_addr.address}")
            print("Commands:")
            print("  send <amount> <trx|usdt>   - Send funds")
            print("  address                    - Show your address")
            print("  balance                    - Show TRX + TRC20 balances")
            print("  history                    - Show last 10 transactions")
            print("  resources                  - Show account resource usage")
            raw = input("> ").strip()
            if not raw:
                continue

            parts = raw.lower().split()
            cmd = parts[0]

            # Address command
            if cmd == "address":
                print(f"🔑  Your address is: {tron_addr.address}\n")
                continue
            
            if cmd == "history":
                print("📜  Fetching last 10 TRC20 transactions (USDT)...")
                txs = await tron_addr.get_last_tx(limit=10)
                for i, tx in enumerate(txs):
                    txid = tx.get("txID")
                    amount = tx.get("raw_data", {}).get("contract", [{}])[0].get("parameter", {}).get("value", {}).get("amount", 0)
                    to = tx.get("raw_data", {}).get("contract", [{}])[0].get("parameter", {}).get("value", {}).get("to_address")
                    from_ = tx.get("raw_data", {}).get("contract", [{}])[0].get("parameter", {}).get("value", {}).get("owner_address")
                    timestamp = tx.get("block_timestamp")
                    print(f"{i}. TXID: {txid}\n   Amount: {amount / DECIMALS:.6f} USDT\n   From: {from_}\n   To: {to}\n   Timestamp: {timestamp}\n")
                continue


            if cmd == "resources":
                print("⚙️  Fetching account resources...")
                resources = await tron_addr.get_resources()
                for k, v in resources.items():
                    print(f"{k.replace('_', ' ').capitalize()}: {v}")
                print()
                continue


            if cmd == "balance":
                print("💰  Fetching balances...")
                balances = await tron_addr.get_balance(trc20_contract_addresses=[USDT_CONTRACT_ADDRESS])
                trx_bal = balances.get("trx_balance", 0)
                trc20 = balances.get("trc20_balances", {})
                usdt_bal = trc20.get(USDT_CONTRACT_ADDRESS, 0)
                
                print(f"Address: {tron_addr.address}")
                print(f"TRX Balance: {trx_bal / DECIMALS:.6f} TRX")
                print(f"USDT Balance: {usdt_bal / DECIMALS:.6f} USDT\n")
                continue


            if cmd != "send" or len(parts) != 3:
                print("❌  Invalid command. Use 'send <amount> <trx|usdt>' or 'address'.")
                continue

            amt_str = parts[1]
            asset = parts[2].lower()
            if asset not in ("trx", "usdt"):
                print("❌  Unknown asset.  Only 'trx' or 'usdt' are allowed.")
                continue

            try:
                amount = Decimal(amt_str)
                if amount <= 0:
                    raise ValueError()
                
            except ValueError:
                print("❌  Invalid amount.  Must be a positive number.")
                continue
            
            amount_sun = int(amount * DECIMALS)

            to_address = input("Recipient address: ").strip()
            if not to_address:
                print("❌  Recipient address cannot be empty.")
                continue

            print(f"⏳  Sending {amount} {asset.upper()} ({amount_sun} sun) to {to_address}...")

            if asset == "trx":
                receipt = await tron_addr.send_trx(to_address, amount_sun)
            else:
                receipt = await tron_addr.send_trc20(to_address, amount_sun, USDT_CONTRACT_ADDRESS)

            print("✅  Transaction submitted. Receipt:")
            print(receipt)
            print()
        except KeyboardInterrupt:
            print("\nBye!")
            break
        except Exception as e:
            print(f"⚠️  Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())

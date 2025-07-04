from decimal import Decimal
from datetime import datetime
from typing import Any


class ConsoleUI:
    @staticmethod
    def show_start_message(address: str) -> None:
        print(
            f"\n🚀 Welcome to the Tron Wallet CLI!\n"
            f"Manage your TRX and USDT assets directly from your terminal.\n\n"
            f"🔑  Your Wallet Address:\n"
            f"    {address}\n\n"
        )


    @staticmethod
    def show_menu() -> str:
        return input(
            "Available Commands:\n"
            "🔹 send <amount> <trx|usdt>   - Send funds to another address\n"
            "🔹 address                    - Show your wallet address\n"
            "🔹 history                    - View your last 10 transasctions\n"
            "🔹 resources                  - Show resource usage (Bandwidth, Energy)\n"
            "🔹 exit                       - Exit the wallet app\n\n"
            "> "
        ).strip()


    @staticmethod
    def show_resources(resources: dict[str, int]) -> None:
        print("⚙️  Fetching account resources...")
        for key, value in resources.items():
            formatted_key = key.replace('_', ' ').capitalize()
            print(f"{formatted_key}: {value}")
        print()


    @staticmethod
    def show_sending_funds_message(amount: Decimal, asset: str, amount_sun: int, to_address: str) -> None:
        print(f"⏳  Sending {amount} {asset.upper()} ({amount_sun} sun) to {to_address}...")


    @staticmethod
    def show_balance(
        address: str,
        balances: dict,
        usdt_contract: str,
        decimal: int,
        ) -> None:
        print("💰  Fetching balances...")

        trx_bal = balances.get("trx_balance", 0)
        usdt_bal = balances.get("trc20_balances", {}).get(usdt_contract, 0)

        print(
            f"Address: {address}\n"
            f"TRX Balance: {trx_bal / decimal:.6f} TRX\n"
            f"USDT Balance: {usdt_bal / decimal:.6f} USDT\n"
        )

    @staticmethod
    def show_transaction_history(transactions: list[dict]) -> None:
        print("📜  Last transactions:")
        if not transactions:
            print("The transaction history is empty")
            return

        for i, tx in enumerate(transactions, start=1):
            print(
                f"{i}. TXID:      {tx['txid']}\n"
                f"   Amount:    {tx['amount']:.6f} {tx['symbol']}\n"
                f"   From:      {tx['from']}\n"
                f"   To:        {tx['to']}\n"
                f"   Timestamp: {tx['timestamp']}\n"
            )


    @staticmethod
    def show_invalid_input_error() -> None:
        print("❌  Invalid command. Use 'send', 'address', 'balance', 'history', 'resources', or 'exit'.")


    @staticmethod
    def show_error(e: Exception) -> None:
        print(f"Unexpected error: {e}")


    @staticmethod
    def show_receipt(receipt: dict[str, Any], network: str) -> None:
        tx_id = receipt.get("id") or receipt.get("transactionID")
        block = receipt.get("blockNumber")
        ts_ms = receipt.get("blockTimeStamp")
        net_use = receipt.get("receipt", {}).get("net_usage")

        try:
            dt = datetime.fromtimestamp(ts_ms / 1000)
            ts_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            ts_str = str(ts_ms)

        base = (
            "https://shasta.tronscan.org" if network == "shasta" else
            "https://nile.tronscan.org"   if network == "nile"   else
            "https://tronscan.org"
        )
        tx_url = f"{base}/#/transaction/{tx_id}"

        print("✅  Transaction Submitted!")
        print("-" * 40)
        print(f" Transaction ID : {tx_id}")
        print(f" Block Number   : {block}")
        print(f" Timestamp      : {ts_str}")
        if net_use is not None:
            print(f" Net Usage      : {net_use} bytes")
        print("-" * 40)
        print(f" View on Explorer: {tx_url}\n")


    @staticmethod
    def show_goodbye() -> None:
        print("👋  Goodbye!")

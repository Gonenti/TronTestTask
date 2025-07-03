from decimal import Decimal
from infrastructure import TronWrapper
from .tron_address import TronAddress
from .console_ui import ConsoleUI

DECIMALS = 10**6

class TronWalletApp:
    def __init__(self, view: ConsoleUI, passphrase: str, provider_url: str,
                 network: str, usdt_contract: str) -> None:
        self.view = view
        self.tron_wrapper = TronWrapper(provider_url=provider_url, network=network)
        self.tron_addr = TronAddress(passphrase=passphrase, tron_wrapper=self.tron_wrapper)
        self.network = network
        self.usdt_contract = usdt_contract


    async def run(self) -> None:
        self.view.show_start_message(address=self.tron_addr.address)
        while True:
            try:
                raw_input = self.view.show_menu()
                if not raw_input:
                    continue

                parts = raw_input.lower().split()
                command = parts[0]

                if command == "exit":
                    self.view.show_goodbye()
                    break

                elif command == "address":
                    await self._cmd_balance()

                elif command == "history":
                    await self._cmd_history()

                elif command == "resources":
                    await self._cmd_resources()

                elif command == "send":
                    await self._cmd_send(parts)

                else:
                    self.view.show_invalid_input_error()

            except Exception as e:
                self.view.show_error(e)


    async def _cmd_balance(self) -> None:
        balances = await self.tron_addr.get_balance(
            trc20_contract_addresses=[self.usdt_contract]
        )
        self.view.show_balance(
            address=self.tron_addr.address,
            balances=balances,
            usdt_contract=self.usdt_contract,
            decimal=DECIMALS
        )


    async def _cmd_history(self) -> None:
        txs = await self.tron_addr.get_last_tx(limit=10)
        self.view.show_transaction_history(txs, DECIMALS)


    async def _cmd_resources(self) -> None:
        resources = await self.tron_addr.get_resources()
        self.view.show_resources(resources)


    async def _cmd_send(self, parts: list[str]) -> None:
        if len(parts) != 3:
            self.view.show_invalid_input_error("Usage: send <amount> <trx|usdt>")
            return

        amt_str, asset = parts[1], parts[2]
        if asset not in ("trx", "usdt"):
            self.view.show_invalid_input_error("Unknown asset. Only 'trx' or 'usdt' are allowed.")
            return

        try:
            amount = Decimal(amt_str)
            if amount <= 0:
                raise ValueError()
        except (ValueError, ArithmeticError):
            self.view.show_invalid_input_error("Invalid amount. Must be a positive number.")
            return

        amount_sun = int(amount * DECIMALS)
        to_address = input("Recipient address: ").strip()
        if not to_address:
            self.view.show_invalid_input_error("Recipient address cannot be empty.")
            return

        self.view.show_sending_funds_message(amount, asset, amount_sun, to_address)
        if asset == "trx":
            receipt = await self.tron_addr.send_trx(to_address, amount_sun)
        else:
            receipt = await self.tron_addr.send_trc20(to_address, amount_sun, self.usdt_contract)

        self.view.show_receipt(receipt, network=self.network)
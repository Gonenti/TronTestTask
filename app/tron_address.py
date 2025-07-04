from typing import Any
from infrastructure import TronWrapper


class TronAddress:
    def __init__(
        self,
        passphrase: str,
        tron_wrapper: TronWrapper
    ):
        self._wrapper = tron_wrapper
        account_detail = tron_wrapper.get_account_from_passphrase_phrase(passphrase)
        self._address = account_detail["base58check_address"]
        self._private_key = account_detail["private_key"]


    @property
    def address(self):
        return self._address


    async def send_trx(
        self, to_address: str, amount_sun: int
    ) -> dict[str, Any]:

        unsigned_txn = await self._wrapper.build_trx_transfer_tx(
            from_address=self.address,
            to_address=to_address,
            amount_sun=amount_sun,
        )
        signed_txn = self._wrapper.sign_transaction(
            unsigned_txn, self._private_key
        )
        receipt = await self._wrapper.execute_transaction(signed_txn)
        return receipt


    async def send_trc20(
        self, to_address: str, amount_sun: int, token_contract_address: str
    ) -> dict[str, Any]:

        unsigned_txn = await self._wrapper.build_trc20_transfer_tx(
            from_address=self.address,
            to_address=to_address,
            amount_sun=amount_sun,
            token_contract_address=token_contract_address
        )
        signed_txn = self._wrapper.sign_transaction(
            unsigned_txn, self._private_key
        )
        receipt = await self._wrapper.execute_transaction(signed_txn)

        return receipt


    async def get_last_tx(
        self, limit: int = 10
    ) -> list[dict[str, Any]]:
        txs = await self._wrapper.get_last_transactions(
            address=self.address,
            limit=limit,
        )
        return txs


    async def get_resources(self) -> dict[str, Any]:
        res: dict[str, Any] = await self._wrapper.get_account_resource(
            self.address
        )
        energy_used = res["TotalEnergyWeight"]
        energy_limit = res["TotalEnergyLimit"]
        net_used = res["TotalNetWeight"]
        net_limit = res["TotalNetLimit"]
        free_net_used = res["freeNetUsed"]
        free_net_limit = res["freeNetLimit"]
        bandwidth = res["bandwidth"]

        return {
            "energy_used": energy_used,
            "energy_limit": energy_limit,
            "net_used": net_used,
            "net_limit": net_limit,
            "free_net_used": free_net_used,
            "free_net_limit": free_net_limit,
            "bandwidth": bandwidth
        }
    

    async def get_balance(
        self,
        trc20_contract_addresses: list[str] = None
    ) -> dict[str, Any]:
        trx_balance = await self._wrapper.get_trx_balance(self._address)

        trc20_balances: dict[str, int] = {}
        if trc20_contract_addresses:
            for contract_addr in trc20_contract_addresses:
                balance = await self._wrapper.get_trc20_balance(
                    self._address,
                    contract_addr
                )
                trc20_balances[contract_addr] = balance

        return {
            "trx_balance": trx_balance,
            "trc20_balances": trc20_balances
        }
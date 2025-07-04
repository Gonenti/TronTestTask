import aiohttp
from tronpy import AsyncTron
from tronpy.keys import PrivateKey
from tronpy.providers import AsyncHTTPProvider
from tronpy.async_tron import AsyncTransaction, AsyncTransactionBuilder
from tronpy.keys import to_base58check_address
from .errors import BroadcastError
from .TRC20_abi import TRC20_ABI

class TronWrapper:

    def __init__(self, provider_url: str, network: str):
        self._provider_url = provider_url
        self._client = AsyncTron(provider=AsyncHTTPProvider(provider_url), network=network)


    async def build_trx_transfer_tx(self, from_address, to_address: str, amount_sun: int) -> AsyncTransaction:
        txb = self._client.trx.transfer(
            from_=from_address,
            to=to_address,
            amount=amount_sun,
        ).fee_limit(100_000_000)
        txn = await txb.build()

        return txn


    async def build_trc20_transfer_tx(
        self,
        from_address: str,
        to_address: str,
        amount: int,
        token_contract_address: str
    ) -> AsyncTransaction:
        contract = await self._client.get_contract(token_contract_address)
        contract.abi = TRC20_ABI
        txb: AsyncTransactionBuilder = contract.functions.transfer(
            to_address,
            amount
        ).with_owner(from_address).fee_limit(100_000_000)
        txn = await txb.build()
        
        return txn


    def sign_transaction(self, unsigned_txn: AsyncTransaction, hex_key: str) -> AsyncTransaction:
        clean_hex = hex_key.replace("0x", "")
        private_bytes = bytes.fromhex(clean_hex)
        private_key = PrivateKey(private_bytes)
        signed_txn = unsigned_txn.sign(private_key)

        return signed_txn


    async def execute_transaction(self, signed_txn: AsyncTransaction):
        try:
            broadcast_response = await signed_txn.broadcast()
            sended_txn = await broadcast_response.wait()

        except Exception as e:
            raise BroadcastError(f"Error when broadcasting to the network: {e}")

        return sended_txn
    

    async def get_last_transactions(
        self,
        address: str,
        limit: int = 10,
        order_by: str = "block_timestamp,desc"
    ) -> list[dict]:
        url = (
            f"{self._provider_url}/v1/accounts/{address}/transactions"
            f"?limit={limit}&order_by={order_by}"
        )
        async with aiohttp.ClientSession() as sess:
            async with sess.get(url, timeout=10) as resp:
                resp.raise_for_status()
                data = (await resp.json()).get("data", [])

        enriched = []
        for tx in data:
            c = tx.get("raw_data", {}).get("contract", [{}])[0]
            ctype = c.get("type")
            val   = c.get("parameter", {}).get("value", {})

            base = {
                "txid":      tx.get("txID"),
                "from":      val.get("owner_address"),
                "to":        val.get("to_address"),
                "timestamp": tx.get("block_timestamp"),
                "symbol":    "?",
                "amount":    0.0,
            }

            if ctype == "TransferContract":
                base["symbol"] = "TRX"
                base["amount"] = val.get("amount", 0) / 1e6

            elif ctype == "TriggerSmartContract":
                hex_addr = val.get("contract_address")
                b58_addr = to_base58check_address(bytes.fromhex(hex_addr))

                contract = await self._client.get_contract(b58_addr)
                contract.abi = TRC20_ABI

                symbol   = await contract.functions.symbol.call()
                decs     = await contract.functions.decimals.call()

                raw = val.get("data", "")
                if isinstance(raw, str) and raw.startswith("0x"):
                    amt = int(raw, 16)
                else:
                    amt = val.get("amount", 0)

                base["symbol"] = symbol
                base["amount"] = amt / (10 ** decs)


            enriched.append(base)

        return enriched


    async def get_account_resource(self, address: str):
        resource = await self._client.get_account_resource(address)
        bandwidth = await self._client.get_bandwidth(address)
        resource['bandwidth'] = bandwidth

        return resource
    

    def get_account_from_passphrase_phrase(self, passphrase: str):
        return self._client.generate_address_from_mnemonic(mnemonic=passphrase)
    

    async def get_trx_balance(self, address: str) -> int:
        account_info = await self._client.get_account(address)
        return account_info.get("balance", 0)


    async def get_trc20_balance(
            self,
            address: str,
            token_contract_address: str
        ) -> int:

        contract = await self._client.get_contract(
            token_contract_address
        )
        contract.abi = TRC20_ABI

        balance = await contract.functions.balanceOf(address)
        return int(balance)
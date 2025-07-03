import asyncio
from app import (
    TronWalletApp,
    ConsoleUI,
    PASSPHRASE,
    PROVIDER_URL, 
    NETWORK, 
    USDT_CONTRACT_ADDRESS
)
async def main() -> None:
    view = ConsoleUI()
    app = TronWalletApp(
        view=view,
        passphrase=PASSPHRASE,
        provider_url=PROVIDER_URL,
        network=NETWORK,
        usdt_contract=USDT_CONTRACT_ADDRESS,
    )
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
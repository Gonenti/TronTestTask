from dotenv import load_dotenv
import os

load_dotenv()

PASSPHRASE = os.getenv("PASSPHRASE")
PROVIDER_URL = os.getenv("PROVIDER_URL")
USDT_CONTRACT_ADDRESS = "TG3XXyExBkPp9nzdajDZsozEu4BkaSJozs"
NETWORK= "shasta"

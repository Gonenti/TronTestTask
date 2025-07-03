# TRON Wallet CLI

A simple command-line interface (CLI) wallet for the TRON blockchain.
Supports sending TRX and USDT (TRC20), checking balances, viewing account resource usage, and listing recent transactions.

---

## 🛠️ Setup Instructions

### 1. Create `.env` file

Create a file named `.env` in the root of the project.

### 2. Fill in the following values:

```env
PROVIDER_URL=https://api.trongrid.io
PASSPHRASE=your wallet passphrase here
```

> 🔐 **Security Tip**: Never share your passphrase. Keep `.env` private and out of version control.

---

### 3. Install dependencies

Make sure you have Python 3.10+ installed.

Install the required packages:

```bash
pip install -r requirements.txt
```

---

### 4. Run the CLI

Start the wallet CLI with:

```bash
python __main__.py
```

---

## 💡 Available Commands

| Command                     | Description                             |
| --------------------------- | --------------------------------------- |
| `send <amount> <trx\|usdt>` | Send TRX or USDT to a recipient address |
| `address`                   | Display your wallet address             |
| `balance`                   | Show TRX and USDT token balances        |
| `resources`                 | Show energy and bandwidth usage         |
| `history`                   | Show last 10 USDT (TRC20) transactions  |
| `CTRL+C`                    | Exit the application                    |

---

## ✅ Example

```bash
> send 1 usdt
Recipient address: TABC123...
⏳  Sending 1 USDT (1000000 sun) to TABC123...
✅  Transaction submitted. Receipt:
{ ...transaction data... }
```

---

## 🔐 Security

This CLI uses your passphrase to derive your private key. Use responsibly and never expose your `.env` file in public repositories.

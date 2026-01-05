# Testing Base RPC URL Connection

## Method 1: Using the curl command (from client)

Replace `{url}` with your actual BASE_RPC_URL from the .env file:

```bash
curl https://base-mainnet.g.alchemy.com/v2/YOUR_API_KEY \
    --request POST \
    --header 'accept: application/json' \
    --header 'content-type: application/json' \
    --data '{"id":1,"jsonrpc":"2.0","method":"eth_blockNumber"}'
```

**Expected response if working:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x1234567"  // Current block number in hex
}
```

## Method 2: Using Python test script

Run the test script I created:

```bash
python test_rpc.py
```

This will:
- Load your .env file
- Test the BASE_RPC_URL connection
- Show the current block number if successful
- Show error messages if there's a problem

## Method 3: Test from Django

You can also test it directly in Django shell:

```bash
python manage.py shell
```

Then run:
```python
from django.conf import settings
from web3 import Web3

rpc_url = settings.BASE_RPC_URL
print(f"RPC URL: {rpc_url[:50]}...")

w3 = Web3(Web3.HTTPProvider(rpc_url))
print(f"Connected: {w3.is_connected()}")
if w3.is_connected():
    print(f"Current block: {w3.eth.block_number}")
```

## Common Issues

1. **Incomplete URL** - Make sure it's the full Alchemy URL
2. **Invalid API Key** - The API key might be expired or wrong
3. **Network Issues** - Check your internet connection
4. **Server Not Restarted** - Restart Django after changing .env






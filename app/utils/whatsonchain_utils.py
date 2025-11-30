from typing import Tuple
from cachetools import cached, TTLCache
from httpx import AsyncClient, Client
from bsv import Transaction

# Import settings and BSV Transaction class
from app.config.settings import settings


# WhatsOnChainUtils class provides utilities for interacting with WhatsOnChain API for BSV blockchain operations
class WhatsOnChainUtils:

    # Base URL for WhatsOnChain API
    BASE_URL = "https://api.whatsonchain.com/v1"
    # Base URL for Gecko API
    BASE_URL_GECKO = "https://api.coingecko.com/api/v3"
    # Blockchain chain identifier
    CHAIN = "bsv"

    # Retrieve all unspent transaction outputs (UTXOs) for a given address
    @staticmethod
    async def get_unspent_utxos(address: str) -> list[dict]:
        url = f"{WhatsOnChainUtils.BASE_URL}/{WhatsOnChainUtils.CHAIN}/main/address/{address}/unspent/all"

        async with AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers=WhatsOnChainUtils._headers())
            resp.raise_for_status()

        data = resp.json()
        return data.get("result", [])

    # Select a single UTXO that has sufficient balance for the required amount
    @staticmethod
    async def select_single_utxo_for_amount(
        address: str,
        amount_satoshis: int,
    ) -> dict:
        utxos = await WhatsOnChainUtils.get_unspent_utxos(address)

        if not utxos:
            raise ValueError("No hay UTXOs para esta dirección en WhatsOnChain")

        # Iterate through UTXOs to find one with enough value
        for utxo in utxos:
            value = utxo.get("value", 0)
            if value >= amount_satoshis:
                return utxo

        raise ValueError(
            f"No hay ningún UTXO con saldo suficiente para enviar {amount_satoshis} satoshis"
        )


    # Get the raw transaction hex for a given transaction ID
    @staticmethod
    async def get_raw_tx_hex(txid: str) -> str:
        url = f"{WhatsOnChainUtils.BASE_URL}/{WhatsOnChainUtils.CHAIN}/main/tx/{txid}/hex"

        async with AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers=WhatsOnChainUtils._headers())
            resp.raise_for_status()

        return resp.text.strip()

    # Get the source transaction and output index for payment construction
    @staticmethod
    async def get_source_tx_and_index_for_payment(
        address: str,
        amount_satoshis: int,
    ) -> Tuple[Transaction, int]:

        # Select a suitable UTXO
        utxo = await WhatsOnChainUtils.select_single_utxo_for_amount(address, amount_satoshis)
        txid = utxo["tx_hash"]
        tx_pos = utxo["tx_pos"]

        # Fetch raw transaction hex
        raw_hex = await WhatsOnChainUtils.get_raw_tx_hex(txid)
        # Parse into Transaction object
        source_tx = Transaction.from_hex(raw_hex)
        if source_tx is None:
            raise ValueError(f"Invalid transaction hex for txid {txid}")

        return source_tx, tx_pos
    
    # Get the total balance (confirmed + unconfirmed) for an address
    @staticmethod
    async def get_balance(address: str) -> int:
        url = f"{WhatsOnChainUtils.BASE_URL}/{WhatsOnChainUtils.CHAIN}/main/address/{address}/balance"
        async with AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers=WhatsOnChainUtils._headers())
            resp.raise_for_status()
        data = resp.json()
        return data.get("confirmed", 0) + data.get("unconfirmed", 0)

    # Convert satoshis to euros using current BSV price
    @staticmethod
    async def convert_satoshis_to_euro(satoshis: int) -> float:
        # Convert satoshis to BSV (1 BSV = 100,000,000 satoshis)
        bsv_amount = satoshis / 100000000 
        # Get current BSV price in EUR
        bsv_price_eur = WhatsOnChainUtils.get_bsv_price_eur()
        # Calculate total value in EUR
        return bsv_amount * bsv_price_eur

    # Get BSV price in EUR from CoinGecko, cached for 5 minutes to reduce 429 errors
    @cached(cache=TTLCache(maxsize=1, ttl=300))
    @staticmethod
    def get_bsv_price_eur() -> float:
        url = f"{WhatsOnChainUtils.BASE_URL_GECKO}/simple/price?ids=bitcoin-cash-sv&vs_currencies=eur"
        with Client(timeout=10.0) as client:
            resp = client.get(url)
            resp.raise_for_status()
        data = resp.json()
        return data.get("bitcoin-cash-sv", {}).get("eur", 0.0)

    # Validate if a transaction is confirmed and matches the expected payment
    @staticmethod
    async def validate_transaction(txid: str, pay_to: str, expected_satoshis: int) -> bool:
        url = f"{WhatsOnChainUtils.BASE_URL}/{WhatsOnChainUtils.CHAIN}/main/tx/{txid}"
        async with AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers=WhatsOnChainUtils._headers())
            if resp.status_code != 200:
                return False
        tx_data = resp.json()
        
        # Check if transaction is confirmed (blockheight != -1)
        if tx_data.get("blockheight", -1) == -1:
            return False  # Not confirmed
        
        # Check transaction outputs for matching address and amount
        for output in tx_data.get("vout", []):
            script_pub_key = output.get("scriptPubKey", {})
            addresses = script_pub_key.get("addresses", [])
            # Verify recipient address and exact amount in BSV
            if pay_to in addresses and output.get("value", 0) == expected_satoshis / 100000000:
                return True
        
        return False

    # Generate headers for WhatsOnChain API requests, including API key if available
    @staticmethod
    def _headers() -> dict:
        api_key = getattr(settings, "WOC_API_KEY", None)
        if api_key:
            return {"woc-api-key": api_key}
        return {}
import httpx
from typing import Tuple

from app.config.settings import settings
from bsv import Transaction


class WhatsOnChainUtils:

    BASE_URL = "https://api.whatsonchain.com/v1"
    CHAIN = "bsv"  # siempre BSV en tu caso

    @classmethod
    def _headers(cls) -> dict:
        api_key = getattr(settings, "WOC_API_KEY", None)
        if api_key:
            return {"woc-api-key": api_key}
        return {}

    @classmethod
    async def get_unspent_utxos(cls, address: str) -> list[dict]:
        url = f"{cls.BASE_URL}/{cls.CHAIN}/main/address/{address}/unspent/all"

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers=cls._headers())
            resp.raise_for_status()

        data = resp.json()
        # data["result"] es la lista de utxos según la doc
        return data.get("result", [])

    @classmethod
    async def select_single_utxo_for_amount(
            cls,
            address: str,
            amount_satoshis: int,
    ) -> dict:
        utxos = await cls.get_unspent_utxos(address)

        if not utxos:
            raise ValueError("No hay UTXOs para esta dirección en WhatsOnChain")

        for utxo in utxos:
            value = utxo.get("value", 0)
            if value >= amount_satoshis:
                return utxo

        raise ValueError(
            f"No hay ningún UTXO con saldo suficiente para enviar {amount_satoshis} satoshis"
        )


    @classmethod
    async def get_raw_tx_hex(cls, txid: str) -> str:
        url = f"{cls.BASE_URL}/{cls.CHAIN}/main/tx/{txid}/hex"

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers=cls._headers())
            resp.raise_for_status()

        # La respuesta es un string plano con el hex
        return resp.text.strip()

    @classmethod
    async def get_source_tx_and_index_for_payment(
            cls,
            address: str,
            amount_satoshis: int,
    ) -> Tuple[Transaction, int]:

        utxo = await cls.select_single_utxo_for_amount(address, amount_satoshis)
        txid = utxo["tx_hash"]
        tx_pos = utxo["tx_pos"]

        raw_hex = await cls.get_raw_tx_hex(txid)
        source_tx = Transaction.from_hex(raw_hex)

        return source_tx, tx_pos
    
    @staticmethod
    async def get_balance(address: str) -> int:
        url = f"https://api.whatsonchain.com/v1/bsv/main/address/{address}/balance"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers=WhatsOnChainUtils._headers())
            resp.raise_for_status()
        data = resp.json()
        return data.get("confirmed", 0) + data.get("unconfirmed", 0)

    @staticmethod
    async def convert_satoshis_to_euro(satoshis: int) -> float:
        bsv_amount = satoshis / 100000000 
        bsv_price_eur = await WhatsOnChainUtils.get_bsv_price_eur()
        return bsv_amount * bsv_price_eur

    @staticmethod
    async def get_bsv_price_eur() -> float:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin-sv&vs_currencies=eur"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
        data = resp.json()
        return data.get("bitcoin-sv", {}).get("eur", 0.0)
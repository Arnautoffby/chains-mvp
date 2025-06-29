"""
/**
 * @file: blockchain.py
 * @description: Сервис проверки транзакций через TronScan API (MVP – заглушка)
 * @dependencies: aiohttp
 * @created: 2025-06-29
 */
"""

from __future__ import annotations

import logging
from typing import List, Dict

import aiohttp

from bot.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class TronScanAPI:
    """Обёртка TronScan API (упрощённая)."""

    def __init__(self) -> None:
        self.base_url: str = settings.tron.api_url.rstrip("/")
        self.api_key = settings.tron.api_key

    async def _request(self, url: str, params: Dict[str, str]) -> Dict:
        headers = {}
        if self.api_key:
            headers["TRON-PRO-API-KEY"] = self.api_key
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers, timeout=10) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def _get_transfers(self, from_address: str, to_address: str) -> List[Dict]:
        """Возвращает список TRC20 переводов USDT from -> to."""

        # TronScan поддерживает endpoint token_trc20/transfers
        url = f"{self.base_url}/token_trc20/transfers"
        params = {
            "fromAddress": from_address,
            "toAddress": to_address,
            "limit": "20",
        }
        data = await self._request(url, params)
        return data.get("token_transfers", []) if isinstance(data, dict) else data

    async def verify_payments(self, from_wallet: str, to_wallets: List[str], amount_usdt: float = 1.0) -> bool:
        """Проверяет перевод USDT на каждый адрес из списка."""

        logger.info("Запрос TronScan: from=%s wallets=%s", from_wallet, to_wallets)

        for to_addr in to_wallets:
            transfers = await self._get_transfers(from_wallet, to_addr)
            ok = any(float(t.get("amount", 0)) >= amount_usdt for t in transfers)
            if not ok:
                logger.info("Платёж не найден %s -> %s", from_wallet, to_addr)
                return False
        return True 
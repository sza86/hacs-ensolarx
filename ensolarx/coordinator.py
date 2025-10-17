# custom_components/ensolarx/coordinator.py
from __future__ import annotations

import asyncio
import logging
import struct
from datetime import timedelta
from typing import Any, Dict, List, Tuple

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import SENSOR_DEFS, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class ModbusError(Exception):
    pass


class EnsolarXCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    """Koordynator odczytów Modbus dla EnsolarX/LE-03MW."""

    def __init__(self, hass: HomeAssistant, client, scan_interval_s: int | None = None) -> None:
        interval = timedelta(seconds=scan_interval_s) if scan_interval_s else UPDATE_INTERVAL
        super().__init__(hass, _LOGGER, name="EnsolarX Coordinator", update_interval=interval)
        self.client = client
        self._defs: List[Dict[str, Any]] = list(SENSOR_DEFS)
        # cache ostatnich poprawnych wartości – ogranicza "miganie" przy pojedynczych timeoutach
        self._last_ok: Dict[str, Any] = {}

        # jeżeli klient ma ustawienia retry, wykorzystamy je; w przeciwnym razie sensowne domyślne
        self._retry_attempts: int = getattr(self.client, "retry_attempts", 2)
        self._retry_delay: float = getattr(self.client, "retry_delay", 0.15)

    async def _async_update_data(self) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        errors: List[Tuple[int, str]] = []

        for d in self._defs:
            addr: int = d["address"]
            dtype: str = d.get("dtype") or d.get("data_type", "uint16")
            name: str = d["name"]
            unit_type: str = d.get("input_type", "holding")  # holding | input
            scale: float = float(d.get("scale", 1.0))
            precision = d.get("precision")
            word_swap: bool = bool(d.get("word_swap", False))
            fallback: bool = bool(d.get("fallback", True))

            count = 1 if dtype in ("uint16", "int16") else 2

            async def _read_once(kind: str) -> List[int]:
                if kind == "holding":
                    return await self.client.read_holding_registers(addr, count)
                return await self.client.read_input_registers(addr, count)

            # próby odczytu: najpierw deklarowany typ, ewentualnie fallback na drugi
            tried_labels: List[str] = []
            regs: List[int] | None = None
            err_primary: Exception | None = None
            err_fallback: Exception | None = None

            # RETRY pętla dla primary
            for attempt in range(1, self._retry_attempts + 1):
                try:
                    regs = await _read_once(unit_type)
                    tried_labels.append(f"{unit_type}[{count}w]")
                    break
                except Exception as e1:
                    err_primary = e1
                    tried_labels.append(f"{unit_type}[{count}w]")
                    if attempt < self._retry_attempts:
                        await asyncio.sleep(self._retry_delay)
            # fallback, jeśli wciąż brak i dozwolony
            if regs is None and fallback:
                other = "input" if unit_type == "holding" else "holding"
                for attempt in range(1, self._retry_attempts + 1):
                    try:
                        regs = await _read_once(other)
                        tried_labels.append(f"{other}[{count}w]")
                        break
                    except Exception as e2:
                        err_fallback = e2
                        tried_labels.append(f"{other}[{count}w]")
                        if attempt < self._retry_attempts:
                            await asyncio.sleep(self._retry_delay)

            if not regs:
                host = getattr(self.client, "host", "?")
                port = getattr(self.client, "port", "?")
                unit_id = getattr(self.client, "unit_id", "?")
                e1_name = type(err_primary).__name__ if err_primary else ""
                e2_name = type(err_fallback).__name__ if err_fallback else ""
                e1_msg = f"{e1_name}: {err_primary}" if err_primary else ""
                e2_msg = f"{e2_name}: {err_fallback}" if err_fallback else ""
                _LOGGER.warning(
                    "EnsolarX: problem z adresem %s: %s addr=%s dtype=%s tried=%s | %s / %s | host=%s port=%s unit_id=%s",
                    addr,
                    name,
                    addr,
                    dtype,
                    ",".join(tried_labels) or "-",
                    e1_msg,
                    e2_msg,
                    host,
                    port,
                    unit_id,
                )
                # jeśli mamy poprzednią dobrą wartość – zostaw ją, żeby nie „migało”
                if name in self._last_ok:
                    results[name] = self._last_ok[name]
                    results[str(addr)] = self._last_ok[name]
                continue

            # dekodowanie + skalowanie
            try:
                value = self._decode_registers(regs, dtype, word_swap)
            except Exception as dec_err:
                errors.append((addr, f"decode error: {dec_err}"))
                # zachowaj poprzednią wartość, jeśli była
                if name in self._last_ok:
                    results[name] = self._last_ok[name]
                    results[str(addr)] = self._last_ok[name]
                continue

            if scale != 1.0:
                value = value * scale
            if precision is not None and isinstance(value, (int, float)):
                value = round(value, int(precision))

            results[name] = value
            results[str(addr)] = value
            self._last_ok[name] = value  # zaktualizuj cache

        if not results and errors:
            raise UpdateFailed("Modbus: żadnego sensora nie udało się odczytać")

        # zagregowane błędy dekodowania – rzadkie, ale niech będą w logu
        for a, msg in errors:
            _LOGGER.warning("EnsolarX: problem z adresem %s: %s", a, msg)

        return results

    @staticmethod
    def _decode_registers(regs: List[int], dtype: str, word_swap: bool) -> Any:
        if dtype == "uint16":
            return int(regs[0] & 0xFFFF)

        if dtype == "int16":
            val = regs[0]
            if val & 0x8000:
                val -= 0x10000
            return int(val)

        if dtype in ("uint32", "float32"):
            if len(regs) < 2:
                raise ValueError("brak dwóch rejestrów dla wartości 32-bit")
            hi, lo = regs[0], regs[1]
            if word_swap:
                hi, lo = lo, hi
            raw = (hi << 16) | lo
            if dtype == "uint32":
                return int(raw & 0xFFFFFFFF)
            return struct.unpack(">f", raw.to_bytes(4, "big"))[0]

        raise ValueError(f"Nieznany data_type: {dtype}")

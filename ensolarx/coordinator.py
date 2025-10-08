from __future__ import annotations
import logging
from typing import Any
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import SENSOR_DEFS, UPDATE_INTERVAL
from .modbus_client import ModbusTcpClient, ModbusError

_LOGGER = logging.getLogger(__name__)

class EnsolarXCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, client: ModbusTcpClient) -> None:
        super().__init__(hass, _LOGGER, name="EnsolarX Coordinator", update_interval=UPDATE_INTERVAL)
        self.client = client
        self._addresses = sorted(set(s["address"] for s in SENSOR_DEFS))

    async def _async_update_data(self) -> dict[str, Any]:
        data = {}
        try:
            for addr in self._addresses:
                regs = await self.client.read_holding_registers(addr, 1)
                data[str(addr)] = regs[0]
            return data
        except (ModbusError, OSError, TimeoutError) as err:
            raise UpdateFailed(f"Modbus error: {err}")

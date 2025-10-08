from __future__ import annotations
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from .const import DOMAIN, CONF_UNIT_ID
from .modbus_client import ModbusTcpClient
from .coordinator import EnsolarXCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    unit_id = entry.data[CONF_UNIT_ID]

    client = ModbusTcpClient(host, port, unit_id=unit_id, timeout=5.0)
    coordinator = EnsolarXCoordinator(hass, client)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {"client": client, "coordinator": coordinator}

    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, [Platform.SENSOR])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, [Platform.SENSOR])
    data = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if data:
        client: ModbusTcpClient = data["client"]
        await client.close()
    return unload_ok

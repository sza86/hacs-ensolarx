from __future__ import annotations
from typing import Any, Dict
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT

from .const import (
    DOMAIN,
    CONF_UNIT_ID,
    CONF_SCAN_INTERVAL,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_UNIT_ID,
    DEFAULT_SCAN_INTERVAL,
)

class EnsolarXConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: Dict[str, Any] | None = None):
        errors: Dict[str, str] = {}
        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}:{user_input[CONF_UNIT_ID]}"
            )
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=f"EnsolarX {user_input[CONF_HOST]}",
                data=user_input
            )

        data_schema = vol.Schema({
            vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
            vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
            vol.Required(CONF_UNIT_ID, default=DEFAULT_UNIT_ID): int,
            vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(int, vol.Range(min=5)),
        })
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

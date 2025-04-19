import voluptuous as vol
from homeassistant import config_entries

DOMAIN = "ensolarx"

class EnsolarXConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="EnsolarX", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Optional("host", default="192.168.86.188"): str,
                vol.Optional("port", default=8899): int,
                vol.Optional("slave_id", default=18): int,
                vol.Optional("scan_interval", default=10): vol.In([5, 10, 30]),
            })
        )

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfElectricPotential, UnitOfElectricCurrent, UnitOfPower, UnitOfTemperature, PERCENTAGE, UnitOfEnergy
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, SENSOR_DEFS
from .coordinator import EnsolarXCoordinator

@dataclass
class EnsolarXSensorDesc:
    name: str
    address: int
    unit: Optional[str] = None
    data_type: str = "uint16"
    scale: float = 1.0
    precision: Optional[int] = None

UNIT_MAP = {
    "V": UnitOfElectricPotential.VOLT,
    "A": UnitOfElectricCurrent.AMPERE,
    "W": UnitOfPower.WATT,
    "Wh": UnitOfEnergy.WATT_HOUR,
    "%": PERCENTAGE,
    "°C": UnitOfTemperature.CELSIUS,
}

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator: EnsolarXCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities = [EnsolarXSensorEntity(coordinator, EnsolarXSensorDesc(**s), entry.entry_id) for s in SENSOR_DEFS]
    async_add_entities(entities)

class EnsolarXSensorEntity(CoordinatorEntity[EnsolarXCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: EnsolarXCoordinator, desc: EnsolarXSensorDesc, entry_id: str) -> None:
        super().__init__(coordinator)
        self._desc = desc
        self._attr_name = desc.name
        self._attr_unique_id = f"{entry_id}_reg_{desc.address}"
        self._attr_native_unit_of_measurement = UNIT_MAP.get(desc.unit, desc.unit)

    @property
    def native_value(self) -> Any:
        if self.coordinator.data is None:
            return None
        raw = self.coordinator.data.get(str(self._desc.address))
        if raw is None:
            return None
        if self._desc.data_type == "int16":
            if raw >= 0x8000:
                raw = raw - 0x10000
        val = float(raw) * float(self._desc.scale if self._desc.scale else 1.0)
        if self._desc.precision is not None:
            return round(val, self._desc.precision)
        if self._desc.unit in ("W", "Wh", None):
            return int(val)
        return val

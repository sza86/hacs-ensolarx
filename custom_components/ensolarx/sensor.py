from __future__ import annotations

from dataclasses import dataclass, fields as dc_fields
from typing import Any, Optional, List

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry

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
    input_type: str = "holding"
    word_swap: bool = False
    fallback: bool = True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: EnsolarXCoordinator = data["coordinator"]

    allowed = {f.name for f in dc_fields(EnsolarXSensorDesc)}
    entities: List[EnsolarXSensorEntity] = [
        EnsolarXSensorEntity(
            coordinator,
            EnsolarXSensorDesc(**{k: v for k, v in s.items() if k in allowed}),
            entry.entry_id,
        )
        for s in SENSOR_DEFS
    ]

    async_add_entities(entities)


class EnsolarXSensorEntity(CoordinatorEntity[EnsolarXCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: EnsolarXCoordinator, desc: EnsolarXSensorDesc, entry_id: str) -> None:
        super().__init__(coordinator)
        self._desc = desc
        self._attr_unique_id = f"{entry_id}_{desc.address}"
        self._attr_name = desc.name
        self._attr_native_unit_of_measurement = desc.unit
        if desc.precision is not None:
            self._attr_suggested_display_precision = desc.precision

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="EnsolarX",
            manufacturer="Endimac",
            model="EnsolarX",
        )

    @property
    def native_value(self) -> Any:
        data = self.coordinator.data or {}
        if self._desc.name in data:
            return data[self._desc.name]
        return data.get(str(self._desc.address))

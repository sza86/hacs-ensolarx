from __future__ import annotations
from datetime import timedelta
from homeassistant.components.sensor import SensorDeviceClass

# Domain **must** be lowercase and match the folder name
DOMAIN = "ensolarx"

CONF_UNIT_ID = "unit_id"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_HOST = "192.168.86.201"
DEFAULT_PORT = 4196
DEFAULT_UNIT_ID = 18
DEFAULT_SCAN_INTERVAL = 10  # seconds (HA minimum is 5)

PLATFORMS = ["sensor"]

# Default coordinator timing; will be overridden per-entry using the chosen scan_interval
UPDATE_INTERVAL = timedelta(seconds=DEFAULT_SCAN_INTERVAL)


# Sensor definitions from EnsolarX docs (subset enabled)
# Supported keys:
#   name, address, unit, data_type ("uint16" | "int16"), scale (float), precision (int)
SENSOR_DEFS = [
    {"name": "Moc wejścia PV1", "address": 1, "unit": "W", "data_type": "uint16"},
    {"name": "Całkowita moc PV", "address": 3, "unit": "W", "data_type": "uint16"},
    {"name": "Napięcie PV1", "address": 4, "unit": "V", "data_type": "uint16", "scale": 0.1, "precision": 1},
    {"name": "Prąd PV1", "address": 5, "unit": "A", "data_type": "int16", "scale": 0.1, "precision": 1},
    {"name": "Napięcie sieci L1", "address": 8, "unit": "V", "data_type": "uint16", "scale": 0.1, "precision": 1},
    {"name": "Moc obciążenia L1", "address": 11, "unit": "W", "data_type": "uint16"},
    {"name": "Całkowita moc obciążenia", "address": 14, "unit": "W", "data_type": "uint16"},
    {"name": "Procent obciążenia", "address": 15, "unit": "%", "data_type": "uint16"},
    {"name": "Napięcie obciążenia", "address": 16, "unit": "V", "data_type": "uint16"},
    {"name": "Napięcie baterii", "address": 17, "unit": "V", "data_type": "uint16", "scale": 0.1, "precision": 1},
    {"name": "Prąd baterii", "address": 18, "unit": "A", "data_type": "int16", "scale": 0.1, "precision": 1},
    {"name": "Status inwertera", "address": 23, "data_type": "uint16"},
    {"name": "Tryb pracy inwertera", "address": 24, "data_type": "uint16"},
    {"name": "Priorytet ładowania", "address": 25, "data_type": "uint16"},
    {"name": "Powrót po niskim napięciu", "address": 29, "unit": "V", "data_type": "uint16", "scale": 0.1, "precision": 1},
    {"name": "Powrót rozładowywania", "address": 30, "unit": "V", "data_type": "uint16", "scale": 0.1, "precision": 1},
    {"name": "Procent baterii (if)", "address": 34, "unit": "%", "data_type": "uint16"},
    {"name": "Prąd baterii (if)", "address": 35, "unit": "A", "data_type": "int16"},
    {"name": "Status ładowania z sieci 1", "address": 36, "data_type": "uint16"},
    {"name": "Status PV = U * I", "address": 45, "data_type": "uint16"},
    {"name": "Temperatura radiatora", "address": 46, "unit": "°C", "data_type": "int16"},
    {"name": "SOC baterii", "address": 57, "unit": "%", "data_type": "uint16", "scale": 0.1, "precision": 1},
    {"name": "Pozostały prąd baterii", "address": 58, "unit": "Ah", "data_type": "int16"},
    {"name": "Różnica napięć celi", "address": 62, "unit": "V", "data_type": "uint16", "scale": 0.001, "precision": 3},
    {"name": "Stan MOSFETów", "address": 63, "data_type": "uint16"},
    {"name": "Napięcie celi 1", "address": 70, "unit": "V", "data_type": "uint16", "scale": 0.001, "precision": 3},
    {"name": "Napięcie celi 2", "address": 71, "unit": "V", "data_type": "uint16", "scale": 0.001, "precision": 3},
    {"name": "Napięcie celi 3", "address": 72, "unit": "V", "data_type": "uint16", "scale": 0.001, "precision": 3},
    {"name": "Napięcie celi 4", "address": 73, "unit": "V", "data_type": "uint16", "scale": 0.001, "precision": 3},
    {"name": "Napięcie celi 5", "address": 74, "unit": "V", "data_type": "uint16", "scale": 0.001, "precision": 3},
    {"name": "Napięcie celi 6", "address": 75, "unit": "V", "data_type": "uint16", "scale": 0.001, "precision": 3},
    {"name": "Napięcie celi 7", "address": 76, "unit": "V", "data_type": "uint16", "scale": 0.001, "precision": 3},
    {"name": "Napięcie celi 8", "address": 77, "unit": "V", "data_type": "uint16", "scale": 0.001, "precision": 3},
    {"name": "Napięcie celi 9", "address": 78, "unit": "V", "data_type": "uint16", "scale": 0.001, "precision": 3},
    {"name": "Napięcie celi 10", "address": 79, "unit": "V", "data_type": "uint16", "scale": 0.001, "precision": 3},
    {"name": "Napięcie celi 11", "address": 80, "unit": "V", "data_type": "uint16", "scale": 0.001, "precision": 3},
    {"name": "Napięcie celi 12", "address": 81, "unit": "V", "data_type": "uint16", "scale": 0.001, "precision": 3},
    {"name": "Napięcie celi 13", "address": 82, "unit": "V", "data_type": "uint16", "scale": 0.001, "precision": 3},
    {"name": "Napięcie celi 14", "address": 83, "unit": "V", "data_type": "uint16", "scale": 0.001, "precision": 3},
    {"name": "Napięcie celi 15", "address": 84, "unit": "V", "data_type": "uint16", "scale": 0.001, "precision": 3},
    {"name": "Napięcie celi 16", "address": 85, "unit": "V", "data_type": "uint16", "scale": 0.001, "precision": 3},
    {"name": "Temperatura BMS 1", "address": 86, "unit": "°C", "data_type": "int16"},
    {"name": "Stan BMS", "address": 87, "data_type": "uint16"},
    {"name": "Przekroczenie napięcia celi", "address": 88, "data_type": "uint16"},
    {"name": "Temperatura akumulatora", "address": 95, "unit": "°C", "data_type": "int16"},
    {"name": "Dziennie: Napięcie sieci", "address": 117, "unit": "V", "data_type": "uint16"},
    {"name": "Dziennie: Moc PV", "address": 118, "unit": "W", "data_type": "uint16"},
    {"name": "Dziennie: Moc wyjściowa", "address": 119, "unit": "W", "data_type": "uint16"},
    {"name": "Dziennie: Napięcie baterii", "address": 120, "unit": "V", "data_type": "uint16"},
    {"name": "Dziennie: Ładowanie", "address": 121, "unit": "W", "data_type": "int16"},
    {"name": "Dziennie: Rozładowanie", "address": 122, "unit": "W", "data_type": "int16"},
    {"name": "Dziennie: Do sieci", "address": 123, "unit": "W", "data_type": "int16"},
    {"name": "Dziennie: Z sieci", "address": 124, "unit": "W", "data_type": "int16"},
    {"name": "Dziennie: Ładowanie PV1", "address": 125, "unit": "Wh", "data_type": "uint16"},
    {"name": "Dziennie: Ładowanie PV2", "address": 126, "unit": "Wh", "data_type": "uint16"}
]

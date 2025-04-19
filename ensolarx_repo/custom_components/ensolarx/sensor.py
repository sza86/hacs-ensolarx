from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.const import CONF_HOST, CONF_PORT
from datetime import timedelta
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusIOException
from asyncio import sleep, Lock
import logging

_LOGGER = logging.getLogger(__name__)
modbus_lock = Lock()

# --- Parsery ---
def parse_protocol(val):
    protocol_names = {
        1: "PI30", 2: "MODBUS", 3: "GROWATT5", 4: "VOLT", 5: "PI18",
        6: "DEYE", 7: "SOFAR", 8: "DEYES", 9: "MODBUS2S", 10: "GROWATT6", 11: "GOODWE",
    }
    return f"{val}.0 - {protocol_names.get(val, 'Nieznany')}"

def parse_firmware(val):
    return f"{(val >> 8) & 0xFF}.{val & 0xFF}"

def parse_wifi(val):
    try:
        major = chr((val >> 8) & 0xFF)
        minor = chr(val & 0xFF)
        return f"1.{major}.{minor}"
    except Exception:
        return "nieznany"

def parse_temp_bms(raw: int) -> float | None:
    if raw == 0:
        return None  # brak danych
    return round((raw - 2731) / 10, 1)



SENSORS = [

    {"name": "Protokół komunikacyjny inwertera", "address": 0, "data_type": "uint16", "parser": parse_protocol},
    {"name": "Moc wejścia PV1", "address": 1, "unit": "W", "data_type": "uint16"},
    # {"name": "Moc wejścia PV2", "address": 2, "unit": "W", "data_type": "uint16"},
    {"name": "Całkowita moc PV", "address": 3, "unit": "W", "data_type": "uint16"},
    {"name": "Napięcie PV1", "address": 4, "unit": "V", "data_type": "uint16", "scale": 0.1, "precision": 1},
    {"name": "Prąd PV1", "address": 5, "unit": "A", "data_type": "int16", "scale": 0.1, "precision": 1},
    # {"name": "Napięcie PV2", "address": 6, "unit": "V", "data_type": "uint16", "scale": 0.1, "precision": 1},
    # {"name": "Prąd PV2", "address": 7, "unit": "A", "data_type": "int16", "scale": 0.1, "precision": 1},
    {"name": "Napięcie sieci L1", "address": 8, "unit": "V", "data_type": "uint16", "scale": 0.1, "precision": 1},
    # {"name": "Napięcie sieci L2", "address": 9, "unit": "V", "data_type": "uint16", "scale": 0.1, "precision": 1},
    # {"name": "Napięcie sieci L3", "address": 10, "unit": "V", "data_type": "uint16", "scale": 0.1, "precision": 1},
    {"name": "Moc obciążenia L1", "address": 11, "unit": "W", "data_type": "uint16"},
    # {"name": "Moc obciążenia L2", "address": 12, "unit": "W", "data_type": "uint16"},
    # {"name": "Moc obciążenia L3", "address": 13, "unit": "W", "data_type": "uint16"},
    {"name": "Całkowita moc obciążenia", "address": 14, "unit": "W", "data_type": "uint16"},
    {"name": "Procent obciążenia", "address": 15, "unit": "%", "data_type": "uint16"},
    {"name": "Napięcie obciążenia", "address": 16, "unit": "V", "data_type": "uint16"},
    {"name": "Napięcie baterii", "address": 17, "unit": "V", "data_type": "uint16", "scale": 0.1, "precision": 1},
    {"name": "Prąd baterii", "address": 18, "unit": "A", "data_type": "int16", "scale": 0.1, "precision": 1},
    {"name": "Status inwertera", "address": 23, "data_type": "uint16"},
    {"name": "Tryb pracy inwertera", "address": 24, "data_type": "uint16"},
    {"name": "Priorytet ładowania", "address": 25, "data_type": "uint16"},
    # {"name": "Napięcie ładowania", "address": 26, "unit": "V", "data_type": "uint16", "scale": 0.1, "precision": 1},
    # {"name": "Napięcie podtrzymania", "address": 27, "unit": "V", "data_type": "uint16", "scale": 0.1, "precision": 1},
    # {"name": "Napięcie odcięcia", "address": 28, "unit": "V", "data_type": "uint16", "scale": 0.1, "precision": 1},
    {"name": "Powrót po niskim napięciu", "address": 29, "unit": "V", "data_type": "uint16", "scale": 0.1, "precision": 1},
    {"name": "Powrót rozładowywania", "address": 30, "unit": "V", "data_type": "uint16", "scale": 0.1, "precision": 1},
    # {"name": "Maks. prąd ładowania całkowity", "address": 31, "unit": "A", "data_type": "uint16"},
    # {"name": "Maks. prąd ładowania z sieci", "address": 32, "unit": "A", "data_type": "uint16"},
    {"name": "Procent baterii (if)", "address": 34, "unit": "%", "data_type": "uint16"},
    {"name": "Prąd baterii (if)", "address": 35, "unit": "A", "data_type": "int16"},
    {"name": "Status ładowania z sieci 1", "address": 36, "data_type": "uint16"},
    # {"name": "Ładowanie z sieci 1 od", "address": 37, "data_type": "uint16"},
    # {"name": "Ładowanie z sieci 1 do", "address": 38, "data_type": "uint16"},
    # {"name": "Prąd ładowania z sieci 1", "address": 39, "unit": "A", "data_type": "uint16"},
    # {"name": "Status ładowania z sieci 2", "address": 40, "data_type": "uint16"},
    # {"name": "Ładowanie z sieci 2 od", "address": 41, "data_type": "uint16"},
    # {"name": "Ładowanie z sieci 2 do", "address": 42, "data_type": "uint16"},
    # {"name": "Prąd ładowania z sieci 2", "address": 43, "unit": "A", "data_type": "uint16"},
    # {"name": "Napięcie nominalne", "address": 44, "unit": "V", "data_type": "uint16"},
    {"name": "Status PV = U * I", "address": 45, "data_type": "uint16"},
    {"name": "Temperatura radiatora", "address": 46, "unit": "°C", "data_type": "int16"},
    # {"name": "Liczba stringów", "address": 47, "data_type": "uint16"},
    # {"name": "Liczba faz", "address": 48, "data_type": "uint16"},
    # {"name": "Nasłonecznienie 1", "address": 54, "unit": "lx", "data_type": "uint16"},
    # {"name": "Nasłonecznienie 2", "address": 55, "unit": "lx", "data_type": "uint16"},
    # {"name": "Nasłonecznienie 3", "address": 56, "unit": "lx", "data_type": "uint16"},
    {"name": "SOC baterii", "address": 57, "unit": "%", "data_type": "uint16", "scale": 0.1, "precision": 1},
    {"name": "Pozostały prąd baterii", "address": 58, "unit": "Ah", "data_type": "int16"},
    # {"name": "Moc baterii", "address": 59, "unit": "W", "data_type": "int16"},
    # {"name": "Minimalne napięcie celi", "address": 60, "unit": "V", "data_type": "uint16", "scale": 0.001, "precision": 3},
    # {"name": "Maksymalne napięcie celi", "address": 61, "unit": "V", "data_type": "uint16", "scale": 0.001, "precision": 3},
    {"name": "Różnica napięć celi", "address": 62, "unit": "V", "data_type": "uint16", "scale": 0.001, "precision": 3},
    {"name": "Stan MOSFETów", "address": 63, "data_type": "uint16"},
    # {"name": "Liczba cykli baterii", "address": 64, "data_type": "uint16"},
    # {"name": "Ostatni zapis: Rok", "address": 65, "data_type": "uint16"},
    # {"name": "Ostatni zapis: Miesiąc", "address": 66, "data_type": "uint16"},
    # {"name": "Ostatni zapis: Dzień", "address": 67, "data_type": "uint16"},
    # {"name": "Ostatni zapis: Godzina", "address": 68, "data_type": "uint16"},
    # {"name": "Ostatni zapis: Minuta", "address": 69, "data_type": "uint16"},
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
    {"name": "Temperatura BMS 1", "address": 86, "unit": "°C", "data_type": "int16", "parser": parse_temp_bms},
    {"name": "Stan BMS", "address": 87, "data_type": "uint16"},
    {"name": "Przekroczenie napięcia celi", "address": 88, "data_type": "uint16"},
    # {"name": "Powrót po przekroczeniu napięcia celi", "address": 89, "data_type": "uint16"},
    # {"name": "Napięcie poniżej normy celi", "address": 90, "data_type": "uint16"},
    # {"name": "Powrót po niskim napięciu celi", "address": 91, "data_type": "uint16"},
    # {"name": "Przekroczenie napięcia pakietu", "address": 92, "data_type": "uint16"},
    # {"name": "Powrót po przekroczeniu napięcia pakietu", "address": 93, "data_type": "uint16"},
    # {"name": "Liczba celi", "address": 94, "data_type": "uint16"},
    {"name": "Temperatura akumulatora", "address": 95, "unit": "°C", "data_type": "int16"},
    # {"name": "Temperatura transformatora", "address": 96, "unit": "°C", "data_type": "int16"},
    # {"name": "Temperatura otoczenia", "address": 97, "unit": "°C", "data_type": "int16"},
    # {"name": "Temperatura PCB", "address": 98, "unit": "°C", "data_type": "int16"},
    # {"name": "BMS: Nominalna pojemność", "address": 99, "unit": "Ah", "data_type": "uint16"},
    # {"name": "BMS: Typ baterii", "address": 100, "data_type": "uint16"},
    # {"name": "RTC: Rok", "address": 101, "data_type": "uint16"},
    # {"name": "RTC: Miesiąc", "address": 102, "data_type": "uint16"},
    # {"name": "RTC: Dzień", "address": 103, "data_type": "uint16"},
    # {"name": "RTC: Godzina", "address": 104, "data_type": "uint16"},
    # {"name": "RTC: Minuta", "address": 105, "data_type": "uint16"},
    # {"name": "RTC: Sekunda", "address": 106, "data_type": "uint16"},
    {"name": "Wersja firmware", "address": 107, "data_type": "uint16", "parser": parse_firmware},
    {"name": "Wersja WiFi", "address": 108, "data_type": "uint16", "parser": parse_wifi},
    # {"name": "10min: Napięcie sieci", "address": 109, "unit": "V", "data_type": "uint16"},
    # {"name": "10min: Moc PV", "address": 110, "unit": "W", "data_type": "uint16"},
    # {"name": "10min: Moc wyjściowa", "address": 111, "unit": "W", "data_type": "uint16"},
    # {"name": "10min: Napięcie baterii", "address": 112, "unit": "V", "data_type": "uint16"},
    # {"name": "10min: Ładowanie baterii", "address": 113, "unit": "W", "data_type": "int16"},
    # {"name": "10min: Rozładowanie baterii", "address": 114, "unit": "W", "data_type": "int16"},
    # {"name": "10min: Do sieci", "address": 115, "unit": "W", "data_type": "int16"},
    # {"name": "10min: Z sieci", "address": 116, "unit": "W", "data_type": "int16"},
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


class EnsolarXSensor(SensorEntity):
    def __init__(self, sensor_config: dict, client: AsyncModbusTcpClient, slave_id: int):
        self._client = client
        self._slave_id = slave_id
        self._address = sensor_config["address"]
        self._name = sensor_config["name"]
        self._data_type = sensor_config.get("data_type", "uint16")
        self._scale = sensor_config.get("scale", 1.0)
        self._offset = sensor_config.get("offset", 0.0)
        self._precision = sensor_config.get("precision", 0)
        self._unit = sensor_config.get("unit")
        self._parser = sensor_config.get("parser")

        self._attr_name = self._name
        self._attr_unique_id = f"ensolarx_{self._address}"
        self._attr_device_class = None
        self._attr_native_unit_of_measurement = self._unit
        self._attr_native_value = None
        self._attr_device_info = {
            "identifiers": {("ensolarx", "ensolarx")},
            "name": "EnsolarX",
            "manufacturer": "ENSolarX",
            "model": "HEMS",
            "sw_version": "Modbus v1.0",
        }

    async def async_update(self):
        try:
            async with modbus_lock:
                response = await self._client.read_holding_registers(
                    address=self._address, count=1, slave=self._slave_id
                )
        except Exception as e:
            _LOGGER.warning(f"[{self._name}] Błąd odczytu: {e}. Próba ponownego połączenia...")
            try:
                await self._client.close()
            except Exception:
                pass
            try:
                await self._client.connect()
                await sleep(1)
                async with modbus_lock:
                    response = await self._client.read_holding_registers(
                        address=self._address, count=1, slave=self._slave_id
                    )
            except Exception as reconnect_error:
                _LOGGER.error(f"[{self._name}] Reconnect nieudany: {reconnect_error}")
                return

        if response and hasattr(response, "registers"):
            val = response.registers[0]
            if self._data_type == "int16" and val > 32767:
                val -= 65536
            if self._parser:
                try:
                    self._attr_native_value = self._parser(val)
                except Exception as parse_err:
                    _LOGGER.error(f"[{self._name}] Błąd parsera: {parse_err}")
                    self._attr_native_value = None
            else:
                val = val * self._scale + self._offset
                self._attr_native_value = round(val, self._precision)
        else:
            _LOGGER.warning(f"[{self._name}] Brak danych z adresu {self._address}")


async def async_setup_entry(hass, entry, async_add_entities):
    host = entry.data.get(CONF_HOST, "192.168.86.188")
    port = entry.data.get(CONF_PORT, 8899)
    slave_id = entry.data.get("slave_id", 18)
    update_interval = entry.data.get("scan_interval", 10)

    client = AsyncModbusTcpClient(host, port=port)
    await client.connect()

    sensors = [EnsolarXSensor(conf, client, slave_id) for conf in SENSORS]
    async_add_entities(sensors)
    _LOGGER.info(f"✅ Dodano {len(sensors)} sensorów EnsolarX")

    async def update_all(now):
        _LOGGER.debug("🔁 Start update_all")
        for i, sensor in enumerate(sensors, start=1):
            try:
                await sensor.async_update()
                sensor.async_write_ha_state()
            except Exception as err:
                _LOGGER.warning(f"[{sensor._name}] Błąd aktualizacji: {err}")
            await sleep(0.5 if i % 10 == 0 else 0.2)

    async_track_time_interval(hass, update_all, timedelta(seconds=update_interval))
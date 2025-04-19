DOMAIN = "ensolarx"

DEFAULT_IP = "192.168.86.188"
DEFAULT_PORT = 8899
DEFAULT_SLAVE_ID = 18
DEFAULT_SCAN_INTERVAL = 10

SENSORS = [
    {"name": "Napięcie L1", "address": 8, "unit": "V"},
    {"name": "Napięcie wyjściowe", "address": 16, "unit": "V"},
    {"name": "Napięcie baterii", "address": 17, "unit": "V"},
]
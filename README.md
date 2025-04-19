# EnsolarX – Integracja Home Assistant

Integracja niestandardowa do odczytu danych z falownika i BMS za pomocą EnsolarX przez Modbus TCP, w pełni zgodna z Home Assistant (2023.x i nowsze). 

Umożliwia automatyczny odczyt napięć, prądów, mocy, danych dziennych, RTC, statusów oraz wielu innych informacji dostępnych przez protokół Modbus TCP.

## 🔧 Funkcje

- Odczyt danych z falownika i BMS za pomocą EnsolarX przez Modbus TCP
- Obsługa wielu rejestrów (napięcia, prądy, moce, dane dzienne, RTC, diagnostyka)
- Konfiguracja przez interfejs Home Assistant (config_flow)
- Automatyczne tworzenie encji na podstawie listy w `sensors.py`
- Możliwość selektywnego włączania/wyłączania czujników

## ⚙️ Konfigurowalne sensory (`sensors.py`)

W pliku `custom_components/ensolarx/sensors.py` znajduje się lista sensorów (`SENSORS`), które integracja odczytuje i wystawia jako encje.

Możesz **włączać/wyłączać** poszczególne czujniki, komentując lub odkomentowując ich definicje za pomocą `#`.

## 🛠️ Instalacja

### Przez HACS

1. HACS → Integracje → ⋮ → Dodaj repozytorium
2. Wklej: https://github.com/sza86/hacs-ensolarx
3. Typ: Integracja → Dodaj → Zainstaluj → Restart HA

### Ręczna

1. Pobierz ZIP
2. Skopiuj do `config/custom_components/ensolarx/`
3. Restart HA → Dodaj integrację → EnsolarX

## 📜 Licencja

MIT License

## 👤 Autor

Integracja stworzona przez [sza86](https://github.com/sza86)


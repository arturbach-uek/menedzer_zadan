## 1. Utworzenie środowiska wirtualnego

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

## 2. Instalacja bibliotek

```bash
pip install -r requirements.txt
```

## 3. Uruchomienie programu

```bash
python3 main.py
```

Po zakończeniu pracy ze środowiskiem wirtualnym można je wyłączyć:

```bash
deactivate
```
# Menadżer zadań

## Cel projektu

Projekt umożliwia zarządzanie listą zadań za pomocą menu w konsoli. 
Pozwala dodawać, wyświetlać i obsługiwać zadania, zapisywać dane w pliku JSON oraz eksportować je do CSV. 
Zawiera również testy automatyczne sprawdzające poprawność działania funkcji.

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

## 4. Uruchomienie testów

```bash
python3 -m pytest
```

## 5. Dezaktywacja środowiska wirtualnego

Po zakończeniu pracy możesz wyłączyć środowisko wirtualne:

```bash
deactivate
```
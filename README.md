# Menadżer zadań

## Cel projektu

Projekt umożliwia zarządzanie listą zadań za pomocą menu w konsoli. 
Pozwala dodawać, wyświetlać i obsługiwać zadania z tagami oraz pokazywać raporty i plan na dziś. 
Dane są zapisywane w bazie SQLite przez SQLAlchemy, a schemat bazy tworzą migracje Alembica. 
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

## 3. Utworzenie bazy danych

Tworzy tabele w bazie `database/task_ord.db`:

```bash
alembic upgrade head
```

Jednorazowo możesz przenieść zadania ze starej bazy `database/tasks.db`:

```bash
python3 -m manager.transfer_data
```

## 4. Uruchomienie programu

```bash
python3 -m manager.main
```

## 5. Uruchomienie testów

```bash
python3 -m pytest
```

## 6. Dezaktywacja środowiska wirtualnego

Po zakończeniu pracy możesz wyłączyć środowisko wirtualne:

```bash
deactivate
```
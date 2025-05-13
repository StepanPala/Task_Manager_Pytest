# Task Manager s MySQL a Pytestem

*Note: English follows*

Jednoduchý správce úkolů s ukládáním do MySQL databáze a testy pomocí Pytest.

## Popis

Program umožňuje spravovat seznam úkolů. Uživatel může přidávat nové úkoly, zobrazovat existující (včetně filtrování podle stavu), aktualizovat stav úkolů a mazat úkoly. Data jsou ukládána do MySQL databáze. Funkčnost je ověřena pomocí sady testů napsaných v Pytestu.

## Použité knihovny a verze Pythonu

Tento program vyžaduje **Python 3.10** a novější (kvůli použití moderních typových anotací).

Knihovny nutné ke spuštění programu a testů jsou uvedeny v souboru `requirements.txt`.
K instalaci externích knihoven je vhodné použít virtuální prostředí.
Knihovny lze nainstalovat následovně:
`pip install -r requirements.txt`

## Používání

### Hlavní aplikace (`src/main.py`)

Program se spouští přímo. Po spuštění se připojí k MySQL databázi (vytvoří ji spolu s potřebnou tabulkou `ukoly`, pokud neexistují) a nabídne interaktivní menu pro správu úkolů.
Ujistěte se, že máte spuštěný MySQL server a zadané správné přihlašovací údaje v `src/main.py` (v základu `user="root"`, `password="1111"`, podle potřeby upravte).

**Spuštění:**
`python src/main.py`

### Testy (`test/test_task_manager.py`)

Testy se spouští pomocí Pytestu z kořenového adresáře projektu. Před spuštěním testů se ujistěte, že máte nainstalovaný Pytest a `mysql-connector-python` (viz `requirements.txt`) a že MySQL server je spuštěný. Testovací databáze (`task_manager_test`) a tabulka (`ukoly`) se vytvoří automaticky, tabulka se po testech smaže. Konfigurace připojení k databázi pro testy je v souboru `test/test_task_manager.py`.
Testy také vyžadují spuštěný MySQL server s přístupem pro uživatele a heslo definované v `test/test_task_manager.py` (v základu `user="root"`, `password="1111"`).

**Spuštění testů:**
`pytest`

## Příklad fungování

### Hlavní aplikace

Ukázka interakce s menu:
```
Databáze 'task_manager' je připravena (byla vytvořena, nebo již existuje).
Tabulka úkolů je připravena v databázi.

Správce úkolů – Hlavní menu:
1. Přidat úkol
2. Zobrazit úkoly
3. Aktualizovat úkol
4. Odstranit úkol
5. Ukončit program
Vyberte možnost (1–5): 1

Zadejte název úkolu: Úkol 1
Zadejte popis úkolu: Popisek 1
Úkol 'Úkol 1' byl úspěšně přidán do databáze.

Hlavní menu:
...
Vyberte možnost (1–5): 5

Konec programu.
Připojení k databázi bylo uzavřeno.
```

### Testy

Ukázka výstupu Pytestu:
```
$ pytest
============================= test session starts ==============================
platform win32 -- Python 3.10.X, pytest-7.X.X, pluggy-1.X.X
rootdir: \cesta\k\projektu
collected 6 items

test\test_task_manager.py ......                                         [100%]

============================== 6 passed in X.XXs ===============================
```

## Autor
Štěpán Pala


# Task Manager with MySQL and Pytest

Simple task manager storing tasks in MySQL database and with tests using Pytest.

## Description

The program can manage a list of tasks. The user can add new tasks, view existing tasks (including filtering by status), update task status, and delete tasks. The data is stored in a MySQL database. Functionality is verified using a suit of Pytest tests.

## Dependencies

This program requires **Python 3.10** or newer (due to use of modern type annotations).

The packages necessary to run the program are specified in `requirements.txt`.  
A virtual environment is recommended to install external packages.  
The dependencies can be installed as follows:  
`pip install -r requirements.txt`

## Usage

### Main (`src/main.py`)

The program is run directly. When it starts, it connects to the MySQL database (creating it along with the necessary table of `ukoly` (tasks) if they do not exist) and offers an interactive menu for task management.
Make sure you have the MySQL server running and the correct login credentials in `src/main.py` (default `user="root"`, `password="1111"`, modify as needed).

**Execution:**
`python src/main.py`

### Tests (`test/test_task_manager.py`)

The tests are run using Pytest from the project root directory. Before running the tests, make sure you have Pytest and `mysql-connector-python` installed (see `requirements.txt`) and that the MySQL server is running. The test database (`task_manager_test`) and table (`ukoly`) are created automatically, the table is dropped after the tests. The configuration of the database connection for tests is in the `test/test_task_manager.py` file.
The tests also require a running MySQL server with user access and a password defined in `test/test_task_manager.py` (by default `user="root"`, `password="1111"`).

**Running tests:**
`pytest`

## Example

### Main
Note: The actual program interface and output are in Czech. The example below is translated for clarity

Menu interaction:
```
Database 'task_manager' is ready (has been created or exists).
The task table is ready in the database.

Task Manager – Main Menu:
1. Add Task
2. View Tasks
3. Update Task
4. Remove Task
5. End Program
Select an option (1–5): 1

Enter Task name: Task 1
Enter Task description: Description 1
Task 'Task 1' has been successfully added to the database.

Main Menu:
...
Select an option (1–5): 5

Exiting program.
Database connection closed.
```

### Tests

Pytest output example:
```
$ pytest
============================= test session starts ==============================
platform win32 -- Python 3.10.X, pytest-7.X.X, pluggy-1.X.X
rootdir: \path\to\your\project
collected 6 items

test\test_task_manager.py ......                                         [100%]

============================== 6 passed in X.XXs ===============================
```

## Author
Štěpán Pala

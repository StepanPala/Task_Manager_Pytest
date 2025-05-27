"""
Konfigurační soubor pro aplikaci a testování Správce úkolů.
Obsahuje konstanty připojení k databázi, názvy tabulek a stavy úkolů.
"""

# Obecné konstanty stavů úkolů
STAV_NEZAHAJENO = "Nezahájeno"
STAV_PROBIHA = "Probíhá"
STAV_HOTOVO = "Hotovo"

# Konfigurace databáze pro hlavní aplikaci
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "1111"
DB_NAME_APP = "task_manager"
TABLE_TASKS = "ukoly"

# Konfigurace databáze pro testy
# Host, přihlašovací jméno a heslo mohou být stejné,
# ale název databáze by měl být odlišný
TEST_DB_NAME = "task_manager_test"
# Název testovací tabulky může být stejný, pokud jej řídí testy
TEST_TABLE_TASKS = "ukoly"

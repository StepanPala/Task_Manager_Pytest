"""
Testy funkcí správy úkolů z modulu main.py pomocí frameworku pytest.
Testují pozitivní a negativní scénáře pro přidání, aktualizaci
a odstranění úkolů.
Používají testovací databázi MySQL.
"""
import mysql.connector
import pytest

from src.main import aktualizovat_ukol, odstranit_ukol, pridat_ukol


@pytest.fixture(scope="function")
def db_conn():
    """
    Pytest fixture pro vytvoření připojení k testovací databázi
    a nastavení testovací tabulky 'ukoly' v databázi 'task_manager_test'.
    Tabulka se po dokončení testů odstraní.
    """
    config = {
        "host": "localhost",
        "user": "root",
        "password": "1111",
        "database":"task_manager_test"
    }
    conn = None
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS task_manager_test")
        cursor.execute("USE task_manager_test") # Výběr databáze
        cursor.execute("DROP TABLE IF EXISTS ukoly")
        cursor.execute("""
            CREATE TABLE ukoly (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL UNIQUE,
                description TEXT NOT NULL,
                status ENUM('Nezahájeno', 'Hotovo', 'Probíhá'),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()

        yield conn  # Poskytnutí testovacím funkcím

    except mysql.connector.Error as err:
        pytest.fail(f"Chyba při připojení k testovací databázi: {err}")
    finally:
        if conn and conn.is_connected():
            cursor = conn.cursor()

            cursor.execute("DROP TABLE IF EXISTS ukoly") # Úklid po testech
            conn.commit()
            cursor.close()
            conn.close()


def test_pridat_positive(db_conn):
    """
    Testuje funkci pridat_ukol() pro úspěšné přidání úkolu.
    Očekává, že úkol bude úspěšně přidán do databáze.
    """
    cursor = None
    try:
        # Definice testovacích dat
        nazev_ukolu = 'Testovací úkol 1'
        popis_ukolu = 'Popis testovacího úkolu 1'
        ocekavany_stav = 'Nezahájeno' # Předpokládaný výchozí stav úkolu

        # Zavolání testované funkce pro přidání úkolu
        task_id = pridat_ukol(db_conn, nazev_ukolu, popis_ukolu)

        # Ověření, že úkol byl úspěšně přidán
        assert task_id is not None and isinstance(
            task_id, int
        ), "Funkce pridat_ukol nevrátila platné ID."

        cursor = db_conn.cursor()
        cursor.execute(
            "SELECT name, description, status FROM ukoly WHERE id = %s", (
                task_id,
            )
        )
        result = cursor.fetchone()
        assert result is not None, "Úkol nebyl přidán do databáze."
        assert result[0] == nazev_ukolu, "Název úkolu v databázi nesouhlasí."
        assert result[1] == popis_ukolu, "Popis úkolu v databázi nesouhlasí."
        assert result[2] == ocekavany_stav, (
            "Stav úkolu v databázi nesouhlasí."
        )
    finally:
        if cursor:
            cursor.close()


def test_pridat_negative(db_conn):
    """
    Testuje funkci pridat_ukol() pro neúspěšné přidání úkolu.
    Očekává, že úkol nebude úspěšně přidán do databáze
    (např. kvůli prázdnému názvu).
    """
    cursor = None
    try:
        # Pokus o přidání úkolu s prázdným názvem
        id_ukolu = pridat_ukol(db_conn, '', 'Popis nevalidního úkolu')

        # Ověření, že funkce vrátila None
        assert id_ukolu is None, (
            "Funkce pridat_ukol vrátila ID pro nevalidní úkol."
        )

        # Ověření, že úkol nebyl přidán do databáze
        cursor = db_conn.cursor()
        cursor.execute(
            "SELECT * FROM ukoly WHERE description = 'Popis nevalidního úkolu'"
        )
        result = cursor.fetchone()
        assert result is None, (
            "Úkol s prázdným názvem byl přidán do databáze, i když neměl."
        )
    finally:
        if cursor:
            cursor.close()


def test_aktualizovat_positive(db_conn):
    """
    Testuje funkci aktualizovat_ukol() pro úspěšnou aktualizaci úkolu.
    Očekává, že úkol bude úspěšně aktualizován v databázi.
    """
    cursor = None
    try:
        # Přidání úkolu pro test aktualizace
        id_ukolu = pridat_ukol(db_conn, 'Úkol k aktualizaci', 'Původní popis')
        assert id_ukolu is not None, (
            "Nepodařilo se přidat úkol pro test aktualizace."
        )
        novy_stav = 'Hotovo'

        # Zavolání testované funkce pro aktualizaci úkolu
        uspech_aktualizace = aktualizovat_ukol(db_conn, id_ukolu, novy_stav)

        # Ověření, že úkol byl úspěšně aktualizován a správně nastaven
        assert uspech_aktualizace, "Funkce aktualizovat_ukol nevrátila úspěch."

        cursor = db_conn.cursor()
        cursor.execute("SELECT status FROM ukoly WHERE id = %s", (id_ukolu,))
        result = cursor.fetchone()
        assert result is not None, (
            "Aktualizovaný úkol nebyl nalezen v databázi."
        )
        assert result[0] == novy_stav, (
            f"Úkol nebyl správně aktualizován na status '{novy_stav}'."
        )
    finally:
        if cursor:
            cursor.close()


def test_aktualizovat_negative(db_conn):
    """
    Testuje funkci aktualizovat_ukol() pro neúspěšnou aktualizaci úkolu.
    Očekává, že úkol nebude úspěšně aktualizován v databázi
    (např. neexistující ID).
    """
    # Definice neexistujícího ID úkolu
    neexistujici_id_ukolu = 99999  # Předpokládáme, že toto ID neexistuje
    # Pokus o aktualizaci úkolu s neexistujícím ID
    uspech_aktualizace = aktualizovat_ukol(
        db_conn, neexistujici_id_ukolu, 'Hotovo'
    )

    # Ověření, že funkce vrátila False
    assert not uspech_aktualizace, (
        "Funkce aktualizovat_ukol vrátila úspěch pro neexistující ID."
    )


def test_odstranit_positive(db_conn):
    """
    Testuje funkci odstranit_ukol() pro úspěšné odstranění úkolu.
    Očekává, že úkol bude úspěšně odstraněn z databáze.
    """
    cursor = None
    try:
        # Přidání úkolu pro test odstranění
        id_ukolu = pridat_ukol(
            db_conn, 'Úkol k odstranění', 'Popis úkolu k odstranění'
        )

        # Ověření, že úkol byl úspěšně odstraněn
        assert id_ukolu is not None, (
            "Nepodařilo se přidat úkol pro test odstranění."
        )

        uspech_odstraneni = odstranit_ukol(db_conn, id_ukolu)
        assert uspech_odstraneni, "Funkce odstranit_ukol nevrátila úspěch."

        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM ukoly WHERE id = %s", (id_ukolu,))
        result = cursor.fetchone()
        assert result is None, "Úkol nebyl správně odstraněn z databáze."
    finally:
        if cursor:
            cursor.close()


def test_odstranit_negative(db_conn):
    """
    Testuje funkci odstranit_ukol() pro neúspěšné odstranění úkolu.
    Očekává, že úkol nebude úspěšně odstraněn z databáze
    (např. neexistující ID).
    """
    # Definice neexistujícího ID úkolu
    neexistujici_id_ukolu = 99999  # Předpokládáme, že toto ID neexistuje
    # Pokus o odstranění úkolu s neexistujícím ID
    uspech_odstraneni = odstranit_ukol(db_conn, neexistujici_id_ukolu)
    # Ověření, že funkce vrátila False
    assert not uspech_odstraneni, (
        "Funkce odstranit_ukol vrátila úspěch pro neexistující ID."
    )

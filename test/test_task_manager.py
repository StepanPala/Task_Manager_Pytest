"""
Testy funkcí správy úkolů z modulu main.py pomocí frameworku pytest.
Testují pozitivní a negativní scénáře pro přidání, aktualizaci
a odstranění úkolů.
Používají testovací databázi MySQL.
"""
import mysql.connector
import pytest

import src.config as config
from src.main import aktualizovat_ukol, odstranit_ukol, pridat_ukol


@pytest.fixture(scope="function")
def db_conn():
    """
    Pytest fixture pro vytvoření připojení k testovací databázi
    a nastavení testovací tabulky 'ukoly' v databázi 'task_manager_test'.
    Tabulka se po dokončení testů odstraní.
    """
    db_conn_data = {
        "host": config.DB_HOST, # Můžeme použít stejné jako pro app
        "user": config.DB_USER, # nebo definovat specifické TEST_DB_HOST atd.
        "password": config.DB_PASSWORD,
    }
    conn = None
    test_cursor = None  # Kurzor, který se poskytne testům
    try:
        conn = mysql.connector.connect(**db_conn_data)
        setup_cursor = conn.cursor() # Kurzor pro nastavení
        setup_cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {config.TEST_DB_NAME}"
        )
        setup_cursor.execute(f"USE {config.TEST_DB_NAME}") # Výběr databáze
        setup_cursor.execute(f"DROP TABLE IF EXISTS {config.TEST_TABLE_TASKS}")
        # Použití konstant pro stavy v ENUM definici
        status_enum_values = (
            f"'{config.STAV_NEZAHAJENO}', '{config.STAV_HOTOVO}', "
            f"'{config.STAV_PROBIHA}'"
        )
        setup_cursor.execute(f"""
            CREATE TABLE {config.TEST_TABLE_TASKS} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                název VARCHAR(50) NOT NULL UNIQUE,
                popis TEXT NOT NULL,
                stav ENUM({status_enum_values}),
                datum_vytvoření TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        setup_cursor.close()

        test_cursor = conn.cursor() # Vytvoření kurzoru pro testy
        yield conn, test_cursor  # Poskytnutí testům

    except mysql.connector.Error as err:
        pytest.fail(f"Chyba při připojení k testovací databázi: {err}")
    finally:
        if test_cursor:
            test_cursor.close() # Uzavření kurzoru poskytnutého testům
        if conn and conn.is_connected():
            cleanup_cursor = conn.cursor() # Nový kurzor pro úklid
            try:
                cleanup_cursor.execute(f"USE {config.TEST_DB_NAME}")
                cleanup_cursor.execute(
                    f"DROP TABLE IF EXISTS {config.TEST_TABLE_TASKS}"
                )
                conn.commit()
            except mysql.connector.Error as e:
                print(f"Chyba během úklidu testovací databáze: {e}")
            finally:
                if cleanup_cursor:
                    cleanup_cursor.close()
            conn.close()


def test_pridat_positive(db_conn):
    """
    Testuje funkci pridat_ukol() pro úspěšné přidání úkolu.
    Očekává, že úkol bude úspěšně přidán do databáze.
    """
    conn, cursor = db_conn # Rozbalení připojení a kurzoru z fixture
    # Definice testovacích dat
    nazev_ukolu = 'Testovací úkol 1'
    popis_ukolu = 'Popis testovacího úkolu 1'
    ocekavany_stav = config.STAV_NEZAHAJENO # Předpokládaný výchozí stav úkolu

    # Zavolání testované funkce pro přidání úkolu
    task_id = pridat_ukol(conn, nazev_ukolu, popis_ukolu)

    # Ověření, že úkol byl úspěšně přidán
    assert task_id is not None and isinstance(
        task_id, int
    ), "Funkce pridat_ukol nevrátila platné ID."

    cursor.execute(
        f"SELECT název, popis, stav FROM {config.TEST_TABLE_TASKS} "
        f"WHERE id = %s", (task_id,)
    )
    result = cursor.fetchone()
    assert result is not None, "Úkol nebyl přidán do databáze."
    assert result[0] == nazev_ukolu, "Název úkolu v databázi nesouhlasí."
    assert result[1] == popis_ukolu, "Popis úkolu v databázi nesouhlasí."
    assert result[2] == ocekavany_stav, (
        "Stav úkolu v databázi nesouhlasí."
    )


def test_pridat_negative(db_conn):
    """
    Testuje funkci pridat_ukol() pro neúspěšné přidání úkolu.
    Očekává, že úkol nebude úspěšně přidán do databáze
    (např. kvůli prázdnému názvu).
    """
    conn, cursor = db_conn
    # Pokus o přidání úkolu s prázdným názvem
    id_ukolu = pridat_ukol(conn, '', 'Popis nevalidního úkolu')

    # Ověření, že funkce vrátila None
    assert id_ukolu is None, (
        "Funkce pridat_ukol vrátila ID pro nevalidní úkol."
    )

    # Ověření, že úkol nebyl přidán do databáze
    cursor.execute(
        f"SELECT * FROM {config.TEST_TABLE_TASKS} "
        f"WHERE popis = 'Popis nevalidního úkolu'"
    )
    result = cursor.fetchone()
    assert result is None, (
        "Úkol s prázdným názvem byl přidán do databáze, i když neměl."
    )


def test_aktualizovat_positive(db_conn):
    """
    Testuje funkci aktualizovat_ukol() pro úspěšnou aktualizaci úkolu.
    Očekává, že úkol bude úspěšně aktualizován v databázi.
    """
    conn, cursor = db_conn
    # Přidání úkolu pro test aktualizace
    id_ukolu = pridat_ukol(conn, 'Úkol k aktualizaci', 'Původní popis')
    assert id_ukolu is not None, (
        "Nepodařilo se přidat úkol pro test aktualizace."
    )
    novy_stav = config.STAV_HOTOVO

    # Zavolání testované funkce pro aktualizaci úkolu
    uspech_aktualizace = aktualizovat_ukol(conn, id_ukolu, novy_stav)

    # Ověření, že úkol byl úspěšně aktualizován a správně nastaven
    assert uspech_aktualizace, "Funkce aktualizovat_ukol nevrátila úspěch."
    cursor.execute(
        f"SELECT stav FROM {config.TEST_TABLE_TASKS} "
        f"WHERE id = %s", (id_ukolu,)
    )
    result = cursor.fetchone()
    assert result is not None, (
        "Aktualizovaný úkol nebyl nalezen v databázi."
    )
    assert result[0] == novy_stav, (
        f"Úkol nebyl správně aktualizován na status '{novy_stav}'."
    )


def test_aktualizovat_negative(db_conn):
    """
    Testuje funkci aktualizovat_ukol() pro neúspěšnou aktualizaci úkolu.
    Očekává, že úkol nebude úspěšně aktualizován v databázi
    (např. neexistující ID).
    """
    conn, _ = db_conn # Kurzor zde není potřeba, ale musíme ho rozbalit
    # Definice neexistujícího ID úkolu
    neexistujici_id_ukolu = 99999  # Předpokládáme, že toto ID neexistuje
    # Pokus o aktualizaci úkolu s neexistujícím ID
    uspech_aktualizace = aktualizovat_ukol(
        conn, neexistujici_id_ukolu, config.STAV_HOTOVO
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
    conn, cursor = db_conn
    # Přidání úkolu pro test odstranění
    id_ukolu = pridat_ukol(
        conn, 'Úkol k odstranění', 'Popis úkolu k odstranění'
    )

    # Ověření, že úkol byl úspěšně odstraněn
    assert id_ukolu is not None, (
        "Nepodařilo se přidat úkol pro test odstranění."
    )

    uspech_odstraneni = odstranit_ukol(conn, id_ukolu)
    assert uspech_odstraneni, "Funkce odstranit_ukol nevrátila úspěch."

    cursor.execute(
        f"SELECT * FROM {config.TEST_TABLE_TASKS} WHERE id = %s", (id_ukolu,)
    )
    result = cursor.fetchone()
    assert result is None, "Úkol nebyl správně odstraněn z databáze."


def test_odstranit_negative(db_conn):
    """
    Testuje funkci odstranit_ukol() pro neúspěšné odstranění úkolu.
    Očekává, že úkol nebude úspěšně odstraněn z databáze
    (např. neexistující ID).
    """
    conn, _ = db_conn # Kurzor zde není potřeba
    # Definice neexistujícího ID úkolu
    neexistujici_id_ukolu = 99999  # Předpokládáme, že toto ID neexistuje
    # Pokus o odstranění úkolu s neexistujícím ID
    uspech_odstraneni = odstranit_ukol(conn, neexistujici_id_ukolu)
    # Ověření, že funkce vrátila False
    assert not uspech_odstraneni, (
        "Funkce odstranit_ukol vrátila úspěch pro neexistující ID."
    )

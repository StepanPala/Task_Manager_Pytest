"""
Správce úkolů v Pythonu, který používá MySQL jako backend.
Tento skript slouží jako ukázková aplikace pro správu úkolů,
která je určená k testování.
Umožňuje uživateli přidávat, zobrazovat, aktualizovat
a odstraňovat úkoly v databázi.
Základní funkce:
- přidání úkolu
- zobrazení všech úkolů
- aktualizace stavu úkolu
- odstranění úkolu
- ošetření neplatného vstupu uživatele
- ošetření prázdného názvu úkolu a popisu
- ošetření duplicitních úkolů
- ošetření prázdného seznamu úkolů
- ošetření neplatného čísla úkolu při odstraňování
"""
import sys

import mysql.connector

# Konstanty stavů úkolů
STAV_NEZAHAJENO = "Nezahájeno"
STAV_PROBIHA = "Probíhá"
STAV_HOTOVO = "Hotovo"


def vytvoreni_databaze() -> bool:
    """
    Vytvoří databázi 'task_manager', pokud ještě neexistuje.
    Používá pevně dané přihlašovací údaje.
    Vrací True, pokud databáze existuje nebo byla úspěšně vytvořena,
    jinak False.
    """
    db_name = "task_manager"
    try:
        # Připojení k MySQL serveru (bez specifikace databáze)
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1111"
        )

        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
        print(
            f"Databáze '{db_name}' je připravena "
            f"(byla vytvořena, nebo již existuje)."
        )
        cursor.close()
        conn.close()

        return True
    except mysql.connector.Error as err:
        print(f"Chyba při vytváření/ověřování databáze '{db_name}': {err}")
        return False


def pripojeni_db():
    """
    Vytvoří připojení k databázi MySQL.
    Vrátí objekt připojení nebo None v případě chyby.
    Pokud dojde k chybě při připojení, vypíše chybovou hlášku.
    """
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="1111",
            database="task_manager"
        )
    except mysql.connector.Error as err:
        print(f"Chyba při připojení k databázi: {err}")
        return None


def vytvoreni_tabulky():
    """
    Ověří existenci tabulky 'ukoly' v databázi a pokud neexistuje,
    vytvoří ji. Pokud tabulka již existuje, zobrazí informaci.
    Tabulka obsahuje sloupce pro ID, název, popis, stav a čas vytvoření.
    """
    db = pripojeni_db()
    if not db:
        return

    cursor = None  # Inicializace pro případ chyby před přiřazením
    try:
        cursor = db.cursor()

        # Ověření, zda tabulka 'ukoly' již existuje
        cursor.execute("SHOW TABLES LIKE 'ukoly'")
        result = cursor.fetchone()

        if result:
            # Tabulka již existuje
            print("Tabulka úkolů je připravena v databázi.")
        else:
            # Tabulka neexistuje, vytvoření nové tabulky
            status_enum_hodnoty = (
                f"'{STAV_NEZAHAJENO}', '{STAV_PROBIHA}', '{STAV_HOTOVO}'"
            )

            print("Tabulka neexistuje, vytvářím ji...")
            cursor.execute(f"""
                CREATE TABLE ukoly (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(50) NOT NULL UNIQUE,
                    description TEXT NOT NULL,
                    status ENUM({status_enum_hodnoty}),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("Tabulka úkolů byla úspěšně vytvořena.")

    except mysql.connector.Error as err:
        print(f"Chyba operace s tabulkou: {err}")
        return
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()


def hlavni_menu():
    """
    Zobrazí hlavní menu s možnostmi výběru podle čísel 1–5.
    """
    print("\nSprávce úkolů – Hlavní menu")
    print("1. Přidat úkol")
    print("2. Zobrazit úkoly")
    print("3. Aktualizovat úkol")
    print("4. Odstranit úkol")
    print("5. Ukončit program")


def pridat_ukol(db_conn, nazev_ukolu: str, popis_ukolu: str):
    """
    Přidá nový úkol do databáze.

    Args:
        db_conn: Připojení k databázi.
        nazev_ukolu (str): Název nového úkolu.
        popis_ukolu (str): Popis nového úkolu.

    Stav úkolu je automaticky nastaven na STAV_NEZAHAJENO.
    Při chybě se provede pokus o rollback a vypíše chybová hláška
    Vrací ID nového úkolu nebo None v případě chyby.
    """
    if not db_conn or not db_conn.is_connected():
        print("Nepodařilo se připojit k databázi.")
        return None

    nazev_ukolu_trimmed = nazev_ukolu.strip()
    popis_ukolu_trimmed = popis_ukolu.strip()

    if not nazev_ukolu_trimmed or not popis_ukolu_trimmed:
        print("Název úkolu a popis nesmí být prázdné.")
        return None

    cursor = None
    try:
        cursor = db_conn.cursor()

        # Nejprve kontroluje, zda úkol s tímto názvem již neexistuje
        cursor.execute(
            "SELECT id FROM ukoly WHERE name = %s", (nazev_ukolu_trimmed,)
        )
        if cursor.fetchone():
            print(
                f"Úkol s názvem '{nazev_ukolu_trimmed}' již existuje. "
                "Zadejte jiný název."
            )
            return None 

        # Pokud neexistuje, provede vložení
        cursor.execute("""
            INSERT INTO ukoly (name, description, status)
            VALUES (%s, %s, %s)
        """, (nazev_ukolu_trimmed, popis_ukolu_trimmed, STAV_NEZAHAJENO))
        db_conn.commit()
        id_ukolu = cursor.lastrowid
        print(f"Úkol '{nazev_ukolu_trimmed}' byl úspěšně přidán do databáze.")
        return id_ukolu

    except mysql.connector.Error as err:
        if db_conn and db_conn.is_connected():
            db_conn.rollback()
        else:
            print(f"Chyba při přidávání úkolu do databáze: {err}")
        return None
    finally:
        if cursor:
            cursor.close()


def zobrazit_ukoly(db_conn, filtr_stavu: str | None = None):
    """
    Zobrazí úkoly z databáze.

    Args:
        db_conn: Připojení k databázi.
        filtr_stavu (str | None, optional): Stav, podle kterého se úkoly
            filtrují ('Nezahájeno', 'Probíhá').
            Pokud je None, zobrazí všechny úkoly.

    Pokud je aktivní filtr a nenalezne žádné odpovídající úkoly,
    zobrazí se upozornění. Úkoly jsou seřazeny podle ID.
    """
    if not db_conn or not db_conn.is_connected():
        print("Nepodařilo se připojit k databázi.")
        return

    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        # Dotaz na základě filtru
        dotaz = "SELECT * FROM ukoly"
        parametry = []
        if filtr_stavu:
            dotaz += " WHERE status = %s"
            parametry.append(filtr_stavu)
        dotaz += " ORDER BY id" # Řazení pro konzistentní výstup

        cursor.execute(dotaz, parametry)
        ukoly = cursor.fetchall()

        if not ukoly:
            if filtr_stavu: # Pokud byl aktivní filtr a nic nenašel
                print(
                    f"\nŽádné úkoly se stavem '{filtr_stavu}' nebyly nalezeny."
                )
            else: # Pokud nebyl aktivní filtr
                print("\nV tabulce nejsou žádné úkoly.")
            return

        print("\nSeznam úkolů:")
        for ukol in ukoly:
            print(
                f"{ukol['id']}. {ukol['name']} – {ukol['description']} "
                f"(Stav: {ukol['status']})"
            )

    except mysql.connector.Error as err:
        print(f"Chyba při načítání úkolů z databáze: {err}")
    finally:
        if cursor:
            cursor.close()


def ziskej_ukoly_pro_vyber(db_conn) -> list[dict]:
    """
    Vrátí seznam úkolů (ID, název, stav) pro výběr.
    V případě chyby při načítání úkolů vrátí prázdný seznam.

    Args:
        db_conn: Připojení k databázi.
    """
    if not db_conn or not db_conn.is_connected():
        print("Nepodařilo se připojit k databázi.")
        return []

    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, status FROM ukoly ORDER BY id")
        ukoly = cursor.fetchall()
        return ukoly
    except mysql.connector.Error as err:
        print(f"Chyba při načítání úkolů pro výběr: {err}")
        return []
    finally:
        if cursor:
            cursor.close()


def priprav_a_zobraz_ukoly_pro_vyber(db_conn, cinnost: str) -> list[int]:
    """
    Získá úkoly, zobrazí je uživateli pro danou činnost
    (aktualizaci/odstranění) a vrátí seznam platných ID.

    Args:
        db_conn: Připojení k databázi.
        cinnost (str): Popis činnosti (k 'aktualizaci', 'odstranění').

    Returns:
        list[int]: Seznam platných ID úkolů.
        Prázdný seznam, pokud nejsou úkoly.
    """
    ukoly_k_vyberu = ziskej_ukoly_pro_vyber(db_conn)
    if not ukoly_k_vyberu:
        print(f"\nŽádné úkoly k {cinnost}.")
        return []

    print(f"\nSeznam úkolů k {cinnost}:")
    platna_id = []
    for ukol_data in ukoly_k_vyberu:
        print(
            f"{ukol_data['id']}. {ukol_data['name']} "
            f"(Aktuální stav: {ukol_data['status']})"
        )
        platna_id.append(ukol_data['id'])
    return platna_id


def aktualizovat_ukol(db_conn, ukol_id: int, novy_stav: str) -> bool:
    """
    Aktualizuje stav existujícího úkolu v databázi.

    Args:
        db_conn: Připojení k databázi.
        ukol_id (int): ID úkolu, který se má aktualizovat.
        novy_stav (str): Nový stav úkolu (STAV_PROBIHA nebo STAV_HOTOVO).

    Vrací True, pokud byla aktualizace úspěšná, jinak False
    Při chybě se provede pokus o rollback a vypíše chybová hláška.
    """
    if not db_conn or not db_conn.is_connected():
        print("Nepodařilo se připojit k databázi.")
        return False

    cursor = None
    try:
        cursor = db_conn.cursor()
        aktualizace = "UPDATE ukoly SET status = %s WHERE id = %s"
        cursor.execute(aktualizace, (novy_stav, ukol_id))
        db_conn.commit()
        if cursor.rowcount > 0:
            print(
                f"Stav úkolu s ID {ukol_id} byl úspěšně aktualizován na "
                f"'{novy_stav}'."
            )
            return True
        print(
            f"Úkol s ID {ukol_id} nebyl nalezen nebo aktualizace selhala."
        )
        return False

    except mysql.connector.Error as err:
        if db_conn:
            db_conn.rollback()
        print(f"Chyba při aktualizaci úkolu v databázi: {err}")
        return False
    finally:
        if cursor:
            cursor.close()


def odstranit_ukol(db_conn, ukol_id: int) -> bool:
    """
    Odstraní úkol z databáze podle jeho ID.

    Args:
        db_conn: Připojení k databázi.
        ukol_id (int): ID úkolu, který se má odstranit.

    Vrací True, pokud bylo odstranění úspěšné, jinak False.
    """
    if not db_conn or not db_conn.is_connected():
        print("Nepodařilo se připojit k databázi.")
        return False

    cursor = None
    try:
        cursor = db_conn.cursor()
        odstraneni_dotazu = "DELETE FROM ukoly WHERE id = %s"
        cursor.execute(odstraneni_dotazu, (ukol_id,))
        db_conn.commit()
        if cursor.rowcount > 0:
            print(f"Úkol s ID {ukol_id} byl úspěšně odstraněn z databáze.")
            return True
        print(
            f"Úkol s ID {ukol_id} nebyl nalezen nebo odstranění selhalo."
        )
        return False

    except mysql.connector.Error as err:
        if db_conn:
            db_conn.rollback()
        print(f"Chyba při odstraňování úkolu z databáze: {err}")
        return False
    finally:
        if cursor:
            cursor.close()


def ziskej_platne_id(vyzva: str, platna_id: list[int]) -> int:
    """
    Získá od uživatele platné ID ze seznamu dostupných ID.
    Opakovaně vyzývá k zadání, dokud není vstup platný.

    Args:
        vyzva (str): Zpráva zobrazená uživateli pro zadání ID.
        platna_id (list[int]): Seznam platných ID,
            ze kterých může uživatel vybírat.

    Returns:
        int: Platné ID zadané uživatelem.
    """
    vybrane_id = -1
    while True:
        try:
            vybrane_id = int(input(vyzva))
            if vybrane_id in platna_id:
                return vybrane_id
            print("Neplatné ID. Zadejte ID ze seznamu.")
        except ValueError:
            print("Neplatný vstup. Zadejte číslo (ID úkolu).")


def ziskej_stav(vyzva: str, povolene_stavy: list[str]) -> str:
    """
    Získá od uživatele platný stav ze seznamu povolených stavů.
    Opakovaně vyzývá k zadání, dokud není vstup platný.

    Args:
        vyzva (str): Zpráva zobrazená uživateli pro zadání stavu.
        povolene_stavy (list[str]): Seznam povolených stavů,
            ze kterých může uživatel vybírat.

    Returns:
        str: Platný stav zadaný uživatelem.
    """
    while True:
        vyber = input(vyzva).strip().capitalize()
        if vyber in povolene_stavy:
            return vyber
        print(f"Neplatný stav. Zadejte jeden z: {', '.join(povolene_stavy)}.")


if __name__ == "__main__":
    vytvoreni_databaze()
    vytvoreni_tabulky()
    db_main_conn = pripojeni_db()

    if not db_main_conn:
        print("Nepodařilo se připojit k databázi. Program bude ukončen.")
        sys.exit(1)

    while True:
        hlavni_menu()

        volba_menu = ""
        while True:
            volba_menu = input("Vyberte možnost (1–5): ")
            if volba_menu in ["1", "2", "3", "4", "5"]:
                break
            print("\nNeplatná volba. Zadejte číslo mezi 1 a 5.")

        if volba_menu == "1":
            novy_nazev = ""
            while True:
                novy_nazev = input("\nZadejte název úkolu: ").strip()
                if not novy_nazev:
                    print("Název úkolu nesmí být prázdný.")
                else:
                    break

            while True:
                novy_popis = input("Zadejte popis úkolu: ").strip()
                if novy_popis:
                    break
                print("\nPopis úkolu nesmí být prázdný.")
            pridat_ukol(db_main_conn, novy_nazev, novy_popis)

        elif volba_menu == "2":
            filtr_zobrazeni = None
            while True:
                chce_filtrovat = input(
                    "\nChcete filtrovat úkoly podle stavu? (ano/ne): "
                ).strip().lower()
                if chce_filtrovat in ['ano', 'ne']:
                    break
                print("Neplatná odpověď. Zadejte 'ano' nebo 'ne'.")

            if chce_filtrovat == 'ano':
                while True:
                    print(
                        f"Dostupné filtry stavů: "
                        f"{STAV_NEZAHAJENO}, {STAV_PROBIHA}"
                    )
                    filtr_zobrazeni = ziskej_stav(
                        "Zadejte stav k vyfiltrování: ",
                        [STAV_NEZAHAJENO, STAV_PROBIHA]
                    )
                    break
            zobrazit_ukoly(db_main_conn, filtr_zobrazeni)

        elif volba_menu == "3":
            platne_id_pro_aktualizaci = priprav_a_zobraz_ukoly_pro_vyber(
                db_main_conn, "aktualizaci"
            )
            if platne_id_pro_aktualizaci:
                id_pro_aktualizaci = ziskej_platne_id(
                    "\nZadejte ID úkolu, který chcete aktualizovat: ",
                    platne_id_pro_aktualizaci
                )

                novy_stav_ukolu = ziskej_stav(
                    f"Zadejte nový stav úkolu "
                    f"({STAV_PROBIHA} nebo {STAV_HOTOVO}): ",
                    [STAV_PROBIHA, STAV_HOTOVO]
                )
                aktualizovat_ukol(
                    db_main_conn, id_pro_aktualizaci, novy_stav_ukolu
                )

        elif volba_menu == "4":
            platne_id_pro_odstraneni = priprav_a_zobraz_ukoly_pro_vyber(
                db_main_conn, "odstranění"
            )
            if platne_id_pro_odstraneni:
                id_pro_odstraneni = ziskej_platne_id(
                    "\nZadejte ID úkolu, který chcete odstranit: ",
                    platne_id_pro_odstraneni
                )

                odstranit_ukol(db_main_conn, id_pro_odstraneni)

        elif volba_menu == "5":
            print("\nKonec programu.")
            break

    if db_main_conn and db_main_conn.is_connected():
        db_main_conn.close()
        print("Připojení k databázi bylo uzavřeno.")

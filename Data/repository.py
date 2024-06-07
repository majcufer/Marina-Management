import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki
import Data.auth_private as auth

from Data.models import charter, crewlist, gost, plovilo, rezervacija, zaposleni, Uporabnik
from typing import List

## V tej datoteki bomo implementirali razred Repo, ki bo vseboval metode za delo z bazo.

class Repo:
    def __init__(self):
        # Ko ustvarimo novo instanco definiramo objekt za povezavo in cursor
        self.conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=5432)
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    def dobi_plovila(self) -> List[plovilo]:
        self.cur.execute("""
            SELECT * FROM plovilo
            order by ime
        """)
         # rezultate querya pretovrimo v python seznam objektov (transkacij)
        plovila = [plovilo.from_dict(t) for t in self.cur.fetchall()]
        return plovila
    
    def dobi_prosta_plovila(self, user_zacetek, user_konec) -> List[plovilo]:
        self.cur.execute("""
            select * from plovilo
            where registracija not IN (
                select plovilo from rezervacija
                where
                    (zacetek <= %s and konec > %s) OR
                    (zacetek > %s and zacetek < %s)
            )
        """, (user_zacetek, user_zacetek, user_zacetek, user_konec))
         # rezultate querya pretovrimo v python seznam objektov (transkacij)
        prosta_plovila = [plovilo.from_dict(t) for t in self.cur.fetchall()]
        return prosta_plovila
    
    def dodaj_rezervacijo(self, r : rezervacija) -> List[rezervacija]:
        self.cur.execute("""
            INSERT into rezervacija(zacetek, konec, gost, plovilo)
            VALUES (%s, %s, %s, %s)
        """, (r.zacetek, r.konec, r.gost, r.plovilo))
        self.conn.commit()

    def dobi_rezervacije_gost(self, gost: str) -> List[rezervacija]:
        self.cur.execute("""
            SELECT * FROM rezervacija
            WHERE gost = %s
        """, (gost,))

        rezervacije = [rezervacija.from_dict(t) for t in self.cur.fetchall()]
        return rezervacije
    
    def dobi_rezervacije_charter(self, charter: str) -> List[rezervacija]:
        self.cur.execute("""
            SELECT id, zacetek, konec, gost, plovilo FROM rezervacija
            LEFT JOIN plovilo ON registracija = plovilo
            WHERE charter = %s
        """, (charter,))

        rezervacije = [rezervacija.from_dict(t) for t in self.cur.fetchall()]
        return rezervacije

    def dodaj_uporabnika(self, uporabnik: Uporabnik):
        self.cur.execute("""
            INSERT into uporabniki(username, role, oseba, password_hash, last_login)
            VALUES (%s, %s, %s, %s, %s)
            """, (uporabnik.username,uporabnik.role, uporabnik.oseba, uporabnik.password_hash, uporabnik.last_login))
        self.conn.commit()


    def dobi_uporabnika(self, username:str) -> Uporabnik:
        self.cur.execute("""
            SELECT username, role, oseba, password_hash, last_login
            FROM uporabniki
            WHERE username = %s
        """, (username,))
         
        u = Uporabnik.from_dict(self.cur.fetchone())
        return u
    
    def posodobi_uporabnika(self, uporabnik: Uporabnik):
        self.cur.execute("""
            Update uporabniki set last_login = %s where username = %s
            """, (uporabnik.last_login,uporabnik.username))
        self.conn.commit()

    def dodaj_gosta(self, gost: gost):
        self.cur.execute("""
            INSERT into gost(emso, ime)
            VALUES (%s, %s)
            """, (gost.emso,gost.ime))
        self.conn.commit()

    def dobi_gosta(self, uporabnik: str) -> gost:
        self.cur.execute("""
            SELECT emso, ime FROM uporabniki
            LEFT JOIN gost ON emso = oseba
            WHERE username = %s
        """, (uporabnik,))
         
        g = gost.from_dict(self.cur.fetchone())
        return g
    
    def dobi_zaposlenega(self, uporabnik: str) -> zaposleni:
        self.cur.execute("""
            SELECT emso, ime, opis, charter FROM uporabniki
            LEFT JOIN zaposleni ON emso = oseba
            WHERE username = %s
        """, (uporabnik,))
         
        z = zaposleni.from_dict(self.cur.fetchone())
        return z
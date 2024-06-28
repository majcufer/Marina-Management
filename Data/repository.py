import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki
import Data.auth_private as auth

from Data.models import charter, crewlist, gost, plovilo, rezervacija, zaposleni, Uporabnik, rezervacijaDto, rezervacijaDto2
from typing import List

## V tej datoteki bomo implementirali razred Repo, ki bo vseboval metode za delo z bazo.

class Repo:
    def __init__(self):
        # Ko ustvarimo novo instanco definiramo objekt za povezavo in cursor
        self.conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=5432)
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    def dobi_plovila_charter(self, charter:str) -> List[plovilo]:
        self.cur.execute("""
            select * from plovilo
            where charter = %s
            order by ime
        """, (charter,))
        # rezultate querya pretovrimo v python seznam objektov (transkacij)
        plovila = [plovilo.from_dict(t) for t in self.cur.fetchall()]
        return plovila
    
    def dobi_prosta_plovila(self, user_zacetek, user_konec, st_ljudi, user_tip) -> List[plovilo]:
        if user_tip in ('Jadrnica', 'Katamaran', 'Motorna jahta'):
            self.cur.execute("""
                select * from plovilo
                where registracija not IN (
                    select plovilo from rezervacija
                    where
                        (zacetek <= %s and konec > %s) OR
                        (zacetek > %s and zacetek < %s)
                ) 
                AND kapaciteta >= %s AND tip = %s
            """, (user_zacetek, user_zacetek, user_zacetek, user_konec, st_ljudi, user_tip))
            # rezultate querya pretovrimo v python seznam objektov (transkacij)
            prosta_plovila = [plovilo.from_dict(t) for t in self.cur.fetchall()]
            return prosta_plovila
        else:
            self.cur.execute("""
                select * from plovilo
                where registracija not IN (
                    select plovilo from rezervacija
                    where
                        (zacetek <= %s and konec > %s) OR
                        (zacetek > %s and zacetek < %s)
                ) 
                AND kapaciteta >= %s
            """, (user_zacetek, user_zacetek, user_zacetek, user_konec, st_ljudi))
            prosta_plovila = [plovilo.from_dict(t) for t in self.cur.fetchall()]
            return prosta_plovila
        
    def create_view(self, user_zacetek, user_konec, st_ljudi, user_tip) -> List[plovilo]:
        if user_tip in ('Jadrnica', 'Katamaran', 'Motorna jahta'):
            self.cur.execute("""
                create or replace view filter as
                select * from plovilo
                where registracija not IN (
                    select plovilo from rezervacija
                    where
                        (zacetek <= %s and konec > %s) OR
                        (zacetek > %s and zacetek < %s)
                ) 
                AND kapaciteta >= %s AND tip = %s
            """, (user_zacetek, user_zacetek, user_zacetek, user_konec, st_ljudi, user_tip))
            self.conn.commit()
        else:
            self.cur.execute("""
                create or replace view filter as
                select * from plovilo
                where registracija not IN (
                    select plovilo from rezervacija
                    where
                        (zacetek <= %s and konec > %s) OR
                        (zacetek > %s and zacetek < %s)
                ) 
                AND kapaciteta >= %s
            """, (user_zacetek, user_zacetek, user_zacetek, user_konec, st_ljudi))
            self.conn.commit()

    def dodaj_rezervacijo(self, r : rezervacija) -> List[rezervacija]:
        self.cur.execute("""
            INSERT into rezervacija(zacetek, konec, gost, plovilo)
            VALUES (%s, %s, %s, %s)
        """, (r.zacetek, r.konec, r.gost, r.plovilo))
        self.conn.commit()

    def odstrani_rezervacijo(self, id):
        self.cur.execute("""
            DELETE from rezervacija
            WHERE id = %s
        """, (id,))
        self.conn.commit()

    def dobi_rezervacije_gost(self, gost: str) -> List[rezervacijaDto]:
        self.cur.execute("""
            SELECT * FROM rezervacija
            left join plovilo on registracija = plovilo
            WHERE gost = %s
        """, (gost,))

        rezervacije = [rezervacijaDto.from_dict(t) for t in self.cur.fetchall()]
        return rezervacije
    
    def dobi_rezervacije_charter(self, charter: str) -> List[rezervacijaDto2]:
        self.cur.execute("""
            SELECT rezervacija.*, plovilo.*, g.ime AS ime_gosta
            FROM rezervacija
            LEFT JOIN plovilo ON rezervacija.plovilo = plovilo.registracija
            LEFT JOIN gost g ON rezervacija.gost = g.emso
            WHERE plovilo.charter = %s
        """, (charter,))

        rezervacije = [rezervacijaDto2.from_dict(t) for t in self.cur.fetchall()]
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
    
    def dobi_zaposlene(self, charter:str) -> List[zaposleni]:
        self.cur.execute("""
            SELECT * FROM zaposleni
            WHERE charter = %s
        """, (charter,))
         
        z = [zaposleni.from_dict(t) for t in self.cur.fetchall()]
        return z
    
    def filtriraj(self, minPrice, maxPrice, minLength, maxLength, minYear, maxYear) -> List[plovilo]:
        self.cur.execute("""
            SELECT * FROM filter
            WHERE
                (cena >= COALESCE(%s, 0)) AND
                (cena <= COALESCE(%s, 10000)) AND
                (dolzina >= COALESCE(%s, 0)) AND
                (dolzina <= COALESCE(%s, 10000)) AND
                (letnik >= COALESCE(%s, 0)) AND
                (letnik <= COALESCE(%s, 10000))
            """, (minPrice, maxPrice, minLength, maxLength, minYear, maxYear))
        prosta_plovila = [plovilo.from_dict(t) for t in self.cur.fetchall()]
        return prosta_plovila
    
    def odstrani_plovilo(self, reg):
        self.cur.execute("""
            DELETE from plovilo
            WHERE registracija = %s;

            DELETE from rezervacija
            WHERE plovilo = %s;
            
        """, (reg, reg))
        self.conn.commit()

    def posodobi_ceno(self, cena, reg):
        self.cur.execute("""
            UPDATE plovilo
            SET cena = %s
            WHERE registracija = %s;
        """, (cena, reg))
        self.conn.commit()
    
    def dodaj_plovilo(self, cena, ime, kapaciteta, letnik, tip, dolzina, charter):
        self.cur.execute("""
            INSERT into plovilo(ime, letnik, kapaciteta, tip, dolzina, charter, cena)
            VALUES (%s, %s, %s, %s, %s, %s, %s); 
        """, (ime, letnik, kapaciteta, tip, dolzina, charter, cena))
        self.conn.commit()

    def odstrani_zaposlenega(self, emso:str):
        self.cur.execute("""
            DELETE from zaposleni
            WHERE emso = %s;
        """, (emso,))
        self.conn.commit()

    def dodaj_zaposlenega(self, ime, emso, pozicija, charter):
        self.cur.execute("""
            INSERT into zaposleni(emso, ime, opis, charter)
            VALUES (%s, %s, %s, %s); 
        """, (emso, ime, pozicija, charter))
        self.conn.commit()
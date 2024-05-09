import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki
import Data.auth_private as auth

from Data.models import charter, crewlist, gost, plovilo, rezervacija, zaposleni
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
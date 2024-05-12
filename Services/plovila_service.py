from Data.repository import Repo
from Data.models import *
from typing import List


# V tej datoteki bomo definirali razred za obdelavo in delo s plovili

class PlovilaService:
    def __init__(self) -> None:
        # Potrebovali bomo instanco repozitorija. Po drugi strani bi tako instanco 
        # lahko dobili tudi kot input v konstrukturju.
        self.repo = Repo()

    def dobi_plovila(self) -> List[plovilo]:
        return self.repo.dobi_plovila()

    def dobi_prosta_plovila(self, user_zacetek, user_konec) -> List[plovilo]:
        return self.repo.dobi_prosta_plovila(user_zacetek, user_konec)

    def naredi_rezervacijo(self, zacetek: date, konec: date, gost: str, plovilo: int) -> None:
        r = rezervacija(
            zacetek=zacetek,
            konec=konec,
            gost=gost,
            plovilo=plovilo
        )
        self.repo.dodaj_rezervacijo(r)
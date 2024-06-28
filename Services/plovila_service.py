from Data.repository import Repo
from Data.models import *
from typing import List


# V tej datoteki bomo definirali razred za obdelavo in delo s plovili

class PlovilaService:
    def __init__(self) -> None:
        # Potrebovali bomo instanco repozitorija. Po drugi strani bi tako instanco 
        # lahko dobili tudi kot input v konstrukturju.
        self.repo = Repo()

    def dobi_prosta_plovila(self, user_zacetek, user_konec, st_ljudi, user_tip) -> List[plovilo]:
        return self.repo.dobi_prosta_plovila(user_zacetek, user_konec, st_ljudi, user_tip)
    
    def create_view(self, user_zacetek, user_konec, st_ljudi, user_tip) -> List[plovilo]:
        self.repo.create_view(user_zacetek, user_konec, st_ljudi, user_tip)

    def naredi_rezervacijo(self, zacetek: date, konec: date, gost: str, plovilo: int) -> None:
        r = rezervacija(
            zacetek=zacetek,
            konec=konec,
            gost=gost,
            plovilo=plovilo
        )
        self.repo.dodaj_rezervacijo(r)

    def dobi_rezervacije_gost(self, gost: str) -> List[rezervacijaDto]:
        return self.repo.dobi_rezervacije_gost(gost)
    
    def dobi_rezervacije_charter(self, charter: str) -> List[rezervacijaDto]:
        return self.repo.dobi_rezervacije_charter(charter)
    
    def filtriraj(self, minPrice, maxPrice, minLength, maxLength, minYear, maxYear) ->  List[plovilo]:
        return self.repo.filtriraj(minPrice, maxPrice, minLength, maxLength, minYear, maxYear)
    
    def odstrani_rezervacijo(self, id):
        self.repo.odstrani_rezervacijo(id)
    
    def dobi_plovila_charter(self, charter:str) -> List[plovilo]:
        return self.repo.dobi_plovila_charter(charter)
    
    def odstrani_plovilo(self, reg):
        self.repo.odstrani_plovilo(reg)

    def posodobi_ceno(self, cena, reg):
        self.repo.posodobi_ceno(cena, reg)
    
    def dodaj_plovilo(self, cena, ime, kapaciteta, letnik, tip, dolzina, charter):
        self.repo.dodaj_plovilo(cena, ime, kapaciteta, letnik, tip, dolzina, charter)
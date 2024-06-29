from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from datetime import date

# V tej datoteki definiramo vse podatkovne modele, ki jih bomo uporabljali v aplikaciji
# Pazi na vrstni red anotacij razredov!

@dataclass_json
@dataclass
class plovilo:
    registracija : int = field(default=0)  # Za vsako polje povemo tip in privzeto vrednost
    ime : str = field(default="")
    letnik: int = field(default=0)
    kapaciteta: int = field(default=0)
    tip: str=field(default="")
    dolzina: float=field(default=0)
    charter:str=field(default="")
    cena:int = field(default=0)


# Za posamezno entiteto ponavadi ustvarimo tudi tako imenovan
# DTO (database transfer object) objekt. To izhaja predvsem iz tega,
# da v sami aplikaciji ponavadi želimo prikazati podatke drugače kot so v bazi.
# Dodatno bi recimo želeli narediti kakšen join in vzeti podatek oziroma stolpec iz druge tabele


@dataclass_json
@dataclass
class charter:
    ime: str = field(default="")

@dataclass_json
@dataclass
class gost:    
    emso : str=field(default="")
    ime : str=field(default="")

@dataclass_json
@dataclass
class rezervacija:
    id: int = field(default=0)
    zacetek: date=field(default=date.today())
    konec: date=field(default=date.today())
    gost: str=field(default="")
    plovilo: int = field(default=0)

@dataclass_json
@dataclass
class zaposleni:
    emso : str=field(default="")
    ime : str=field(default="")
    opis: str=field(default="")
    charter: str=field(default="")

@dataclass_json
@dataclass
class zaposleniDto:
    emso : str=field(default="")
    ime : str=field(default="")
    opis: str=field(default="")
    charter: str=field(default="")
    username: str=field(default="")

@dataclass_json
@dataclass
class Uporabnik:
    username: str = field(default="")
    role: str = field(default="")
    oseba: str = field(default="")
    password_hash: str = field(default="")
    last_login: str = field(default="")

@dataclass
class UporabnikDto:
    username: str = field(default="")
    role: str = field(default="")
    oseba: str = field(default="")

@dataclass_json
@dataclass
class rezervacijaDto:
    id: int = field(default=0)
    zacetek: date=field(default=date.today())
    konec: date=field(default=date.today())
    gost: str=field(default="")
    plovilo: int = field(default=0)
    ime : str = field(default="")
    letnik: int = field(default=0)
    kapaciteta: int = field(default=0)
    tip: str=field(default="")
    dolzina: float=field(default=0)
    charter:str=field(default="")
    cena:int = field(default=0)

@dataclass_json
@dataclass
class rezervacijaDto2:
    id: int = field(default=0)
    zacetek: date=field(default=date.today())
    konec: date=field(default=date.today())
    gost: str=field(default="")
    plovilo: int = field(default=0)
    ime : str = field(default="")
    letnik: int = field(default=0)
    kapaciteta: int = field(default=0)
    tip: str=field(default="")
    dolzina: float=field(default=0)
    charter:str=field(default="")
    cena:int = field(default=0)
    ime_gosta: str=field(default="")
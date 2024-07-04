from Presentation.bottleext import get, post, run, request, template, redirect, static_file, url, response, template_user
from functools import wraps

from Services.plovila_service import PlovilaService
from Services.auth_service import AuthService
import os

service = PlovilaService()
auth = AuthService()

# privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)

def cookie_required(f):
    """
    Dekorator, ki zahteva veljaven piškotek. Če piškotka ni, uporabnika preusmeri na stran za prijavo.
    """
    @wraps(f)
    def decorated( *args, **kwargs):
        cookie = request.get_cookie("uporabnik")
        if cookie:
            return f(*args, **kwargs)
        return template("prijava.html",uporabnik=None, rola=None, napaka="Potrebna je prijava!")
        
    return decorated

@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='Presentation/static')


@get('/')
def index():
    """
    Domača stran.
    """
    rola = request.get_cookie("rola")
    uporabnik = request.get_cookie("uporabnik")
    return template('index.html', rola = rola, uporabnik=uporabnik)

@post('/iskanje/')
def iskanje():
    """
    Stran s prostimi plovili za določeno obdobje.
    """   
    user_zacetek = request.forms.getunicode("user_zacetek")
    user_konec = request.forms.getunicode("user_konec")
    st_ljudi = request.forms.getunicode("st_ljudi")
    user_tip = request.forms.getunicode("user_tip")

    minP = request.forms.getunicode("minPrice")
    maxP = request.forms.getunicode("maxPrice")
    minL = request.forms.getunicode("minLength")
    maxL = request.forms.getunicode("maxLength")
    minY = request.forms.getunicode("minYear")
    maxY = request.forms.getunicode("maxYear")

    minPrice = int(minP or 0) if minP != '' else None
    maxPrice = int(maxP or 0) if maxP != '' else None
    minLength = int(minL or 0) if minL != '' else None
    maxLength = int(maxL or 0) if maxL != '' else None
    minYear = int(minY or 0) if minY != '' else None
    maxYear = int(maxY or 0) if maxY != '' else None

    rola = request.get_cookie("rola")
    uporabnik = request.get_cookie("uporabnik")

    if any([minPrice, maxPrice, minLength, maxLength, minYear, maxYear]):
        prosta_plovila = service.filtriraj(user_zacetek,user_konec,st_ljudi,user_tip,minPrice,maxPrice,minLength,maxLength,minYear,maxYear)
    else:   
        prosta_plovila = service.dobi_prosta_plovila(user_zacetek, user_konec, st_ljudi, user_tip)
        
    return template('prosta_plovila.html', prosta_plovila = prosta_plovila, user_zacetek=user_zacetek, user_konec=user_konec,
                    rola=rola, uporabnik=uporabnik, st_ljudi=st_ljudi, user_tip=user_tip)

@post('/naredi_rezervacijo')
@cookie_required
def naredi_rezervacijo():
    uporabnik = request.get_cookie("uporabnik")

    zacetek = request.forms.getunicode("user_zacetek")
    konec = request.forms.getunicode("user_konec")
    gost = auth.dobi_gosta(uporabnik).emso
    plovilo = request.forms.getunicode("plovilo")

    service.naredi_rezervacijo(zacetek, konec, gost, plovilo)

    redirect(url('moja_marina'))

@post('/prijava')
def prijava():
    """
    Prijavi uporabnika v aplikacijo. Če je prijava uspešna, ustvari piškotke o uporabniku in njegovi roli.
    Drugače sporoči, da je prijava neuspešna.
    """
    username = request.forms.get('username')
    password = request.forms.get('password')

    if not auth.obstaja_uporabnik(username):
        return template("prijava.html", rola=None, napaka="Uporabnik s tem imenom ne obstaja")

    prijava = auth.prijavi_uporabnika(username, password)
    if prijava:
        response.set_cookie("uporabnik", username)
        response.set_cookie("rola", prijava.role)
        
        redirect(url('index'))

    else:
        return template("prijava.html", uporabnik=None, rola=None, napaka="Neuspešna prijava. Napačno geslo ali uporabniško ime.")
    
@get('/odjava')
def odjava():
    """
    Odjavi uporabnika iz aplikacije. Pobriše piškotke o uporabniku in njegovi roli.
    """
    
    response.delete_cookie("uporabnik")
    response.delete_cookie("rola")
    
    return template('index.html', uporabnik=None, rola=None, napaka=None)

@get('/registracija')
def registracija_get():
    return template('registracija.html', rola=None, uporabnik=None)

@post('/registracija')
def registracija_post():
    """
    Registracija uporabnika. Dodajanje uporabnika v tabelo uporabniki.
    """
    ime = request.forms.getunicode('ime')
    username = request.forms.get('username')
    password = request.forms.get('password')
    role = request.forms.get('rola')
    emso = request.forms.get('emso')

    auth.dodaj_uporabnika(username, role, emso, password)
    auth.dodaj_gosta(emso, ime)
    
    redirect(url('index'))
    
@get('/moja_marina')
@cookie_required
def moja_marina():
    """
    Uporabniške strani, ki se razlikujejo glede na to ali je uporabnik, gost ali zaposlen
    """
    rola = request.get_cookie("rola")
    uporabnik = request.get_cookie("uporabnik")

    if rola == 'gost':
        gost = auth.dobi_gosta(uporabnik)
        rezervacije = service.dobi_rezervacije_gost(gost.emso)
        
        return template('moja_marina_gost.html', rola=rola, uporabnik=uporabnik, gost=gost,
                        rezervacije=rezervacije)
    elif rola == 'charter':
        zaposleni = auth.dobi_zaposlenega(uporabnik)
        rezervacije = service.dobi_rezervacije_charter(zaposleni.charter)

        return template('moja_marina_charter.html', rola=rola, uporabnik=uporabnik,
                        rezervacije=rezervacije, zaposleni=zaposleni)
    
@post('/odstrani_rezervacijo')
def odstrani_rezervacijo():
    id = request.forms.getunicode('id')

    service.odstrani_rezervacijo(id)

    redirect(url('moja_marina'))

@get('/upravljaj_plovila')
@cookie_required
def upravljaj_plovila():
    """
    Uporabniška stran, kjer direktor charterja lahko upravlja plovila
    """
    rola = request.get_cookie("rola")
    uporabnik = request.get_cookie("uporabnik")

    zaposleni = auth.dobi_zaposlenega(uporabnik)
    plovila = service.dobi_plovila_charter(zaposleni.charter)

    return template('charter_plovila.html', rola=rola, uporabnik=uporabnik,
                        zaposleni=zaposleni, plovila=plovila)

@post('/odstrani_plovilo')
def odstrani_plovilo():
    reg = request.forms.getunicode('reg')

    service.odstrani_plovilo(reg)

    redirect(url('upravljaj_plovila'))

@post('/posodobi_ceno')
def posodobi_ceno():
    cena = request.forms.getunicode('cena')
    reg = request.forms.getunicode('reg')

    if cena:
        service.posodobi_ceno(cena, reg)
    else:
        pass

    redirect(url('upravljaj_plovila'))

@post('/dodaj_plovilo')
def dodaj_plovilo():
    cena = request.forms.getunicode('cena')
    ime = request.forms.getunicode('ime')
    kapaciteta = request.forms.getunicode('kapaciteta')
    letnik = request.forms.getunicode('letnik')
    tip = request.forms.getunicode('tip')
    dolzina = request.forms.getunicode('dolzina')
    charter = request.forms.getunicode('charter')

    service.dodaj_plovilo(cena, ime, kapaciteta, letnik, tip, dolzina, charter)
    
    redirect(url('upravljaj_plovila'))

@get('/upravljaj_zaposlene')
@cookie_required
def upravljaj_zaposlene():
    """
    Uporabniška stran, kjer direktor charterja lahko upravlja zaposlene
    """
    rola = request.get_cookie("rola")
    uporabnik = request.get_cookie("uporabnik")

    zaposleni_user = auth.dobi_zaposlenega(uporabnik)
    zaposleni = auth.dobi_zaposlene(zaposleni_user.charter)

    return template('zaposleni.html', rola=rola, uporabnik=uporabnik,
                    zaposleni_user=zaposleni_user, zaposleni=zaposleni)

@post('/odstrani_zaposlenega')
def odstrani_zaposlenega():
    emso = request.forms.getunicode('emso')

    auth.odstrani_zaposlenega(emso)

    redirect(url('upravljaj_zaposlene'))

@post('/dodaj_zaposlenega')
def dodaj_zaposlenega():
    ime = request.forms.getunicode('ime')
    emso = request.forms.getunicode('emso')
    pozicija = request.forms.getunicode('pozicija')
    charter = request.forms.getunicode('charter')

    auth.dodaj_zaposlenega(ime, emso, pozicija, charter)

    redirect(url('upravljaj_zaposlene'))

@post('/dodeli_dostop')
def dodeli_dostop():
    username = request.forms.getunicode('username')
    password = request.forms.getunicode('password')
    emso = request.forms.getunicode('emso')

    auth.dodaj_uporabnika(username, 'charter', emso, password)

    redirect(url('upravljaj_zaposlene'))


if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER, debug=True)
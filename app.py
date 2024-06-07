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
def poisci_proste():
    """
    Stran s prostimi plovili za določeno obdobje.
    """   
    user_zacetek = request.forms.getunicode("user_zacetek")
    user_konec = request.forms.getunicode("user_konec")

    rola = request.get_cookie("rola")
    uporabnik = request.get_cookie("uporabnik")

    prosta_plovila = service.dobi_prosta_plovila(user_zacetek, user_konec)  
        
    return template('prosta_plovila.html', prosta_plovila = prosta_plovila, user_zacetek=user_zacetek, user_konec=user_konec, rola=rola, uporabnik=uporabnik)

@post('/naredi_rezervacijo')
@cookie_required
def naredi_rezervacijo():
    uporabnik = request.get_cookie("uporabnik")

    zacetek = request.forms.getunicode("user_zacetek")
    konec = request.forms.getunicode("user_konec")
    gost = auth.dobi_gosta(uporabnik).emso
    plovilo = request.forms.getunicode("plovilo")

    service.naredi_rezervacijo(zacetek, konec, gost, plovilo)

    redirect(url('/'))

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
        
        redirect(url('/'))

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
    
    redirect(url('/'))
    
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
    elif rola =='admin':
        pass
    elif rola == 'charter':
        zaposleni = auth.dobi_zaposlenega(uporabnik)
        rezervacije = service.dobi_rezervacije_charter(zaposleni.charter)

        return template('moja_marina_charter.html', rola=rola, uporabnik=uporabnik,
                        rezervacije=rezervacije, zaposleni=zaposleni)

#auth.dodaj_uporabnika('admin', 'admin', None, 'admin')
#auth.dodaj_uporabnika('nika', 'charter', 100506505234, 'nika')

if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER, debug=True)
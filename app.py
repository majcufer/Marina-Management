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
    return template('index.html')

@post('/iskanje/')
def poisci_proste():
    """
    Stran s prostimi plovili za določeno obdobje.
    """   
    user_zacetek = request.forms.getunicode("user_zacetek")
    user_konec = request.forms.getunicode("user_konec")

    prosta_plovila = service.dobi_prosta_plovila(user_zacetek, user_konec)  
        
    return template('prosta_plovila.html', prosta_plovila = prosta_plovila, user_zacetek=user_zacetek, user_konec=user_konec)

@post('/naredi_rezervacijo')
@cookie_required
def naredi_rezervacijo():
    
    zacetek = request.forms.getunicode("user_zacetek")
    konec = request.forms.getunicode("user_konec")
    gost = request.get_cookie("oseba")
    plovilo = request.forms.getunicode("plovilo")

    service.naredi_rezervacijo(zacetek, konec, gost, plovilo)

    redirect(url('/rezervacije'))

@get('/rezervacije')
def rezervacije():
    """
    Stran z rezervacijami.
    """
    rezervacije = service.dobi_rezervacije()

    return template('rezervacije.html', rezervacije=rezervacije)

@post('/prijava')
def prijava():
    """
    Prijavi uporabnika v aplikacijo. Če je prijava uspešna, ustvari piškotke o uporabniku in njegovi roli.
    Drugače sporoči, da je prijava neuspešna.
    """
    username = request.forms.get('username')
    password = request.forms.get('password')

    if not auth.obstaja_uporabnik(username):
        return template("prijava.html", napaka="Uporabnik s tem imenom ne obstaja")

    prijava = auth.prijavi_uporabnika(username, password)
    if prijava:
        response.set_cookie("uporabnik", username)
        response.set_cookie("rola", prijava.role)
        response.set_cookie("oseba", prijava.oseba)
        
        # redirect v večino primerov izgleda ne deluje
        #redirect(url('/rezervacije'))

        # Uporabimo kar template, kot v sami "index" funkciji

        # transakcije = service.dobi_transakcije()        
        #return template('rezervacije.html', rezervacije = rezervacije)
        
    else:
        return template("prijava.html", uporabnik=None, rola=None, oseba=None, napaka="Neuspešna prijava. Napačno geslo ali uporabniško ime.")

@get('/odjava')
def odjava():
    """
    Odjavi uporabnika iz aplikacije. Pobriše piškotke o uporabniku in njegovi roli.
    """
    
    response.delete_cookie("uporabnik")
    response.delete_cookie("rola")
    response.delete_cookie("oseba")
    
    return template('prijava.html', uporabnik=None, rola=None, oseba=None, napaka=None)



auth.dodaj_uporabnika('maj', 'admin', '280297500987', 'maj')

if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER, debug=True)
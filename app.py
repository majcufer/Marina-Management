from Presentation.bottleext import get, post, run, request, template, redirect, static_file, url, response, template_user

from Services.plovila_service import PlovilaService
import os
service = PlovilaService()

# privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)

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
        
    return template('prosta_plovila.html', prosta_plovila = prosta_plovila)


if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER, debug=True)
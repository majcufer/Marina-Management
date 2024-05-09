import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki
import auth_private as auth
from bs4 import BeautifulSoup

conn = psycopg2.connect(
    database=auth.db,
    host=auth.host, 
    user=auth.user,  
    password=auth.password, 
    port=5432
    )

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

#################################################################################################

def string_to_number(s):
    numeric_part = ''.join(c for c in s if c.isdigit() or c == '.')
    number = float(numeric_part)
    return number

from Data.data_import.raw_data import html_code

# Parse the HTML
soup = BeautifulSoup(html_code, 'html.parser')

# Find all <li> tags with class 'search-result-wrapper'
yacht_listings = soup.find_all('li', class_='search-result-wrapper')

yachts_details = {}

# Iterate over each yacht listing and extract data
for listing in yacht_listings:
    try:
      # Extract yacht name
      yacht_name_element = listing.find('h3', class_='search-result-middle__heading')
      yacht_name = yacht_name_element.find('span', recursive=False).get_text(strip=True)

      # Extract yacht details
      details_names = listing.select('.search-result-middle__params-name li')
      details_values = listing.select('.search-result-middle__params-value li')
      yacht_details = {name.get_text(strip=True): value.get_text(strip=True) 
                      for name, value in zip(details_names, details_values)
                      if name.text.strip() not in ['Glavno jadro', 'Kabine']}

      # Extract yacht price
      yacht_price = listing.find('span', class_='price-box__price').text.strip()

      yacht_charter_element = listing.find('div', class_='search-result-right__top')
      yacht_charter = yacht_charter_element.find('img')['alt'] if yacht_charter_element else "Not available"


      yachts_details[yacht_name] = {
              'letnik': yacht_details["Leto"],
              'kapaciteta': yacht_details["Oseb"],
              'tip': yacht_details["Tip plovila"],
              'dolzina': string_to_number(yacht_details["Dolžina"]),
              'charter': yacht_charter,
              'cena': string_to_number(yacht_price)
          }
      
      # Print extracted data

      print("Uspešno")
    except:
       pass


for ime in yachts_details.keys():
        letnik = int(yachts_details[ime]['letnik'])
        kapaciteta = int(yachts_details[ime]['kapaciteta'])
        tip = yachts_details[ime]['tip']
        dolzina = yachts_details[ime]['dolzina']
        charter = yachts_details[ime]['charter']
        cena = int(yachts_details[ime]['cena'])

        cur.execute("""
                    INSERT into plovilo(ime, letnik, kapaciteta, tip, dolzina, charter, cena)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (ime, letnik, kapaciteta, tip, dolzina, charter, cena))

        conn.commit()

#################################################################################################

from raw_data import gosti

for ime in gosti.keys():
    emso = gosti[ime]

    cur.execute("""
                INSERT into gost(emso, ime)
                VALUES (%s, %s)
                """, (emso, ime))

    conn.commit()

#################################################################################################

from raw_data import zaposleni

for ime in zaposleni.keys():
    emso = zaposleni[ime]['emso']
    opis = zaposleni[ime]['opis']
    charter = zaposleni[ime]['charter']

    cur.execute("""
                INSERT into zaposleni(emso, ime, opis, charter)
                VALUES (%s, %s, %s, %s)
                """, (emso, ime, opis, charter))

    conn.commit()

#################################################################################################
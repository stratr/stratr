from bs4 import BeautifulSoup
import urllib
import requests
import pymongo
from pymongo import MongoClient

# Mongo-yhteys:
client = MongoClient('localhost', 27017)
db = client.twiitit
ke_collection = db.kansanedustajat2


# Eduskunnan sivujen scrape:
r = urllib.request.urlopen('https://www.eduskunta.fi/FI/kansanedustajat/nykyiset_kansanedustajat/Sivut/default.aspx').read()
soup = BeautifulSoup(r, "html.parser")

kansanedustajat_div = soup.find("div", class_="col-xs-8")

# print(kansanedustajat_div)

# Hae kansanedustajien tiedot:

for div in kansanedustajat_div:
    try:
        tr_objektit = div.findAll("tr")
        for tr in tr_objektit:
            # Nimi
            linkki = tr.find("a")
            ke_nimi = linkki.get_text()
            
            # Puolue    
            td_objektit = tr.findAll("td")
            ke_puolue = td_objektit[5].get_text()

            # Tiedot mongoon
            ke_collection.insert({"nimi": ke_nimi, "puolue": ke_puolue})
            
    except AttributeError:
        print()

print("done")




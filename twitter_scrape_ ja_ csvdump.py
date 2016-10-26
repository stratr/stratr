import tweepy
import json
from tweepy import OAuthHandler
import pymongo
from pymongo import MongoClient
import csv

# Twitter tiedot: 
consumer_key = ''
consumer_secret = ''
access_token = ''
access_secret = ''
 
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
 
api = tweepy.API(auth)

# Mongo-yhteys:
client = MongoClient('localhost', 27017)
db = client.twiitit
ke_collection = db.kansanedustajat2

vaikeat_nimet = {}

# Twitter-listan nimien läpikäynti:
for member in tweepy.Cursor(api.list_members, 'SuomenEduskunta', 'Kansanedustajat', skip_status=True).items():
    try:
        # Tarkistetaan löytyykö nimi tietokannasta, jos ei, niin tulostetaan tiedot
        if ke_collection.find({"nimi": member.name}).count() > 0:
            ke_collection.find_one_and_update(
                {"nimi": member.name},
                {"$set": {"twittername": member.screen_name, "twitterid": member.id_str}}
            )

        # Jos ei löytynyt oikealla nimellä, niin kokeilee tietokannasta, onko väärä kirjoitusasu jo korjattu
        elif ke_collection.find({"nimi_twitter": member.name}).count() > 0:
            ke_collection.find_one_and_update(
                {"nimi_twitter": member.name},
                {"$set": {"twittername": member.screen_name, "twitterid": member.id_str}}
            )
        
        # Lisää nimet, joita ei löytynyt, dictionaryyn
        else:
            vaikeat_nimet[member.name] = [member.screen_name, member.id_str]
            print(member.name, member.screen_name, member.id_str, "\n")
    except BaseException:
        print("hups")
    
#print(vaikeat_nimet)

# Vaikeiden nimien kirjoittaminen csv-tiedostoon:
with open('vaikeat_nimet.csv', 'w', newline='') as csvfile:
    fieldnames = ['nimi', 'nimi_twitter', 'twittername', 'twitterid']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=",", dialect="excel")
    
    writer.writeheader()
    for key, value in vaikeat_nimet.items():
        writer.writerow({'nimi': "", 'nimi_twitter': key, 'twittername': value[0], 'twitterid': value[1]})


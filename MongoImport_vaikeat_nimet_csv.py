import pymongo
from pymongo import MongoClient
import csv


# Mongo-yhteys:
client = MongoClient('localhost', 27017)
db = client.twiitit
ke_collection = db.kansanedustajat2

# csv_reader:
with open('vaikeat_nimet_edit.csv') as csvfile:
    csvreader = csv.DictReader(csvfile, delimiter=",")
    for row in csvreader:
        if ke_collection.find({"nimi": row['nimi']}).count() > 0:
            ke_collection.find_one_and_update(
                {"nimi": row['nimi']},
                {"$set": {"nimi_twitter": row['nimi_twitter'], "twittername": row['twittername'], "twitterid": row['twitterid']}}
            )
        # Tulosta nimet, joita ei saatu mongoon
        else:
            print(row['nimi'], row['nimi_twitter'], row['twittername'], row['twitterid'])

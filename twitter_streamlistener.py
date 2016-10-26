import time
import tweepy
import io
import json
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from pymongo import MongoClient
import os

# TWITTER TUNNUKSET JA OAUTH ------------------------------------------
ckey = ''
consumer_secret = ''
access_token_key = ''
access_token_secret = ''

auth = OAuthHandler(ckey, consumer_secret) #OAuth object
auth.set_access_token(access_token_key, access_token_secret)

api = tweepy.API(auth)
 
start_time = time.time() #grabs the system time

client = MongoClient('localhost', 27017)



# USER LIST -----------------------------------------------------------
kansanedustajat_db = client.twiitit
ke_collection = kansanedustajat_db.kansanedustajat_master

# Eduskunnan twitter-listan nimien läpikäynti (kertoo onko tietokanta ajantasalla):
no_find = False
for member in tweepy.Cursor(api.list_members, 'SuomenEduskunta', 'Kansanedustajat', skip_status=True).items():

    # Tarkistetaan löytyykö nimi tietokannasta, muuten tulostetaan
    if ke_collection.find({"twitterid": member.id_str}).count() == 0:
        no_find = True
        print("Käyttäjää", member.name + ", " + member.id_str, "ei löytynyt tietokannasta.\n")
        
if no_find == False:
    print("Kaikki eduskunnan Twitter-listan käyttäjät ovat seurannassa.")
    
# Käyttäjälistan muodostus seurantaa varten:
user_list = [] # Seurattujen lista on aluksi tyhjä

# Valitsee, mitä tietoja otetaan, halutaan vain twitterid, ei _id
cursor = ke_collection.find({}, {"_id": 0, "twitterid": 1})

for document in cursor:
    document_list = list(filter(None, document.values()))
    user_list.extend(document_list)

print("Näitä kansanedustajien ID:tä seurataan:\n\n", user_list, "\n")



# STREAM LISTENER -----------------------------------------------------
class listener(StreamListener):
 
    def __init__(self, start_time, time_limit, db_client):
 
        self.time = start_time
        self.limit = time_limit
        self.tweet_data = []
        self.db_client = db_client
 
    def on_data(self, data):
        
        response = json.loads(data)
        if 'user' in response: # tarkistetaan, onko api:sta tullut viesti twiitti, vai joku muu
            if response["user"]["id_str"] in user_list: # tarkistaa, onko twiittaajana seurattu henkilö itse, vai onko esim. retweetattu hänen twiitti
                print("Twiitti käyttäjältä " + response["user"]["name"] + ", ID:" + response["user"]["id_str"] + ":\n")
                #print('"{}"\n'.format(response["text"], "utf-8", errors="ignore"))#ignore, koska muuten kaatuu hymiöihin errors="ignore"
                try:
                    self.save_to_database(response)
                    return True
                except BaseException as e:
                    print ('failed ondata,', str(e))
                    time.sleep(5)
                    pass
        else:
            print(response, "\n") # jos on joku muu viesti, niin printataan
     
    def save_to_database(self, data):
        db = self.db_client['twiitit']
        collection = db['kansanedustajien_twiitit']
        collection.insert_one(data)
 
    def on_error(self, status):
 
        print (status) #tässä on joku error: "statuses not defined"

listenerTesti = listener(start_time, time_limit=20, db_client = client)

twitterStream = Stream(auth, listenerTesti) #määrittele tähän time_limit
twitterStream.filter(follow=user_list)  #call the filter method to run the Stream Object

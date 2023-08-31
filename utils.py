from passlib.hash import pbkdf2_sha256
from datetime import datetime
from config import Config
from googlemaps import Client, places

def create_hash_passwrod(new_password):
    hash_password = pbkdf2_sha256.hash(new_password + Config.SALT)
    return hash_password

def compare_hash_password(new_password, old_password):
    compare_password = pbkdf2_sha256.verify(new_password + Config.SALT, old_password)
    return compare_password

def create_file_name():
    return datetime.now().isoformat().replace(':','_').replace('.', '_') + '.jpg'

def date_formatting(data):
    if data == None:
        return 
    
    date_list = ['date', 'createdAt', 'updatedAt']
    for date in date_list:
        if date in data and data[date] != None:
            data[date] = data[date].isoformat()
    
    return data

def decimal_formatting(data):
    if data == None:
        return
    
    date_list = ['rating', 'storeLat', 'storeLng', 'distance']
    for date in date_list:
        if date in data:
            data[date] = float(data[date])
    
    return data


def place_format(place_list):
    result_list = []
    for place in place_list['results']:
        result_list.append({
            'storeLat' : place['geometry']['location']['lat'],
            'storeLng' : place['geometry']['location']['lng'],
            'storeName' : place['name'],
            'storeAddr' : place['vicinity']
        })
    # next_page_token
    # results = list
        #   geometry : location
            # lat, lng
        # vicinity
        # name

    return place_list['next_page_token'] if 'next_page_token' in place_list else '', result_list

def get_google_place(lat, lng, keyword):
    gmaps = Client(key=Config.GOOGLE_KEY)
    
    place_list = places.places_nearby(client=gmaps, location=(lat ,lng), 
                                      radius=1500, keyword=keyword, language='ko')

    return place_format(place_list)

def get_google_next_token(token):
    gmaps = Client(key=Config.GOOGLE_KEY)
    
    place_list = places.places_nearby(client=gmaps, language='ko', page_token=token)
 
    return place_format(place_list) 


def get_random_login_code():
    return datetime.now().isoformat().replace(':','').replace('.', '')
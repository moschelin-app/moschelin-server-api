from passlib.hash import pbkdf2_sha256
from datetime import datetime
from config import Config

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
    
    date_list = ['rating', 'storeLat', 'storeLng']
    for date in date_list:
        if date in data:
            data[date] = float(data[date])
    
    return data
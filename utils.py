from passlib.hash import pbkdf2_sha256
from config import Config

def create_hash_passwrod(new_password):
    hash_password = pbkdf2_sha256.hash(new_password + Config.SALT)
    return hash_password

def compare_hash_password(new_password, old_password):
    compare_password = pbkdf2_sha256.verify(new_password + Config.SALT, old_password)
    return compare_password
import hashlib
import random
from django.utils.crypto import get_random_string

def activation_code(user_name , length=32):
    salt = get_random_string(32)
    usernamesalt = (user_name+salt).encode('utf8')
    return hashlib.sha1(usernamesalt).hexdigest()[:length]

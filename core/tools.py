import hashlib
import random
from django.utils.crypto import get_random_string

def team_activation_code(team_name , length=32):
    salt = get_random_string(32)
    teamnamesalt = (team_name+salt).encode('utf8')
    return hashlib.sha1(teamnamesalt).hexdigest()[:length]

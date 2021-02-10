def create_activation_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

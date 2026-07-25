import random, string

def get_url_token(n: int =7) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=n))
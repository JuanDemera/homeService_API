import random

def generate_otp(length=6):
    """
    Genera un OTP numérico del largo especificado
    """
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])
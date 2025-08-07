import secrets

def generate_otp(length=6):
    """
    Genera un OTP numérico del largo especificado, usando un generador seguro
    """
    return ''.join([str(secrets.randbelow(10)) for _ in range(length)])

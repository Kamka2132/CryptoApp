import math

def extended_gcd(a, b):
    """Rozszerzony Algorytm Euklidesa."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def mod_inverse(a, m):
    """Odwrotność modularna a^-1 mod m."""
    gcd, x, _ = extended_gcd(a, m)
    if gcd != 1:
        return None
    return (x % m + m) % m

def encrypt_text(text: str, a: int, b: int, alphabet_size: int = 26) -> str:
    """Szyfrowanie: c = (a * p + b) mod n"""
    if math.gcd(a, alphabet_size) != 1:
        raise ValueError("Klucz 'a' musi być względnie pierwszy z rozmiarem alfabetu!")
    
    result = []
    for char in text:
        if char.isalpha():
            is_upper = char.isupper()
            base = ord('A') if is_upper else ord('a')
            p = ord(char) - base
            c = (a * p + b) % alphabet_size
            result.append(chr(c + base))
        else:
            result.append(char)
    return "".join(result)

def decrypt_text(text: str, a: int, b: int, alphabet_size: int = 26) -> str:
    """Deszyfrowanie: p = a^-1 * (c - b) mod n"""
    a_inv = mod_inverse(a, alphabet_size)
    if a_inv is None:
        raise ValueError("Klucz 'a' nie posiada odwrotności modularnej!")
    
    result = []
    for char in text:
        if char.isalpha():
            is_upper = char.isupper()
            base = ord('A') if is_upper else ord('a')
            c = ord(char) - base
            p = (a_inv * (c - b)) % alphabet_size
            result.append(chr(p + base))
        else:
            result.append(char)
    return "".join(result)
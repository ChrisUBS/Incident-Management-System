from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64
import hashlib

# Crea una clave de 32 bytes (256 bits) desde un string
KEY = hashlib.sha256(b'123').digest()

def encrypt(text):
    iv = get_random_bytes(16)
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    # Aplicar padding antes de cifrar
    padded_text = pad(text.encode('utf-8'), AES.block_size)
    encrypted = cipher.encrypt(padded_text)
    return base64.b64encode(iv + encrypted).decode('utf-8')

def decrypt(encrypted_text):
    try:
        raw = base64.b64decode(encrypted_text)
        if len(raw) < 16:
            raise ValueError("Encrypted text is too short to contain a valid IV.")
        iv = raw[:16]
        cipher = AES.new(KEY, AES.MODE_CBC, iv)
        # Desencriptar el texto
        decrypted = cipher.decrypt(raw[16:])
        # Quitar el padding después de desencriptar
        decrypted_text = unpad(decrypted, AES.block_size).decode('utf-8')
        return decrypted_text
    except Exception as e:
        print(f"Error decrypting: {e}")
        return None

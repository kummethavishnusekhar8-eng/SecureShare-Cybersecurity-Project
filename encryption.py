from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# Learning project only.
# In production, store this key securely.
KEY = get_random_bytes(32)

def encrypt_file(input_file, output_file):
    cipher = AES.new(KEY, AES.MODE_EAX)

    with open(input_file, "rb") as f:
        data = f.read()

    ciphertext, tag = cipher.encrypt_and_digest(data)

    with open(output_file, "wb") as f:
        f.write(cipher.nonce)
        f.write(tag)
        f.write(ciphertext)


def decrypt_file(input_file, output_file):

    with open(input_file, "rb") as f:
        nonce = f.read(16)
        tag = f.read(16)
        ciphertext = f.read()

    cipher = AES.new(KEY, AES.MODE_EAX, nonce=nonce)

    data = cipher.decrypt_and_verify(ciphertext, tag)

    with open(output_file, "wb") as f:
        f.write(data)
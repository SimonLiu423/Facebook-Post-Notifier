from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import getpass
import os


def pad(data):
    block_size = AES.block_size
    padding = block_size - len(data) % block_size
    return data + padding.to_bytes(1, byteorder='big') * padding


def encrypt_file(file_path, key):
    iv = get_random_bytes(AES.block_size)

    cipher = AES.new(key, AES.MODE_CBC, iv)

    with open(file_path, 'rb') as file:
        plaintext = file.read()

    padded_plaintext = pad(plaintext)

    ciphertext = cipher.encrypt(padded_plaintext)

    with open(file_path + '.enc', 'wb') as file:
        file.write(iv)
        file.write(ciphertext)

    print(f"Encryption successful. Encrypted file: {file_path}.enc")


if __name__ == "__main__":
    passwd = getpass.getpass(prompt="Enter password (16 chars):")
    if len(passwd) > 16:
        passwd = passwd[:16]
        print("Password length greater than 16, truncated.")
    elif len(passwd) < 16:
        passwd += ' ' * (16 - len(passwd))
        print("Password length less than 16, filled with blanks.")
    passwd = bytes(passwd.encode('utf-8'))

    file_to_encrypt = os.path.abspath(os.path.dirname(__file__) + '/../../../' + 'config.yaml')
    if not os.path.exists(file_to_encrypt):
        print("File not found.")
    else:
        encrypt_file(file_to_encrypt, passwd)

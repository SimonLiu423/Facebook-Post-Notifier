from Crypto.Cipher import AES
import yaml
import getpass


def decrypt(encrypted_file):
    with open(encrypted_file, 'rb') as f:
        iv = f.read(AES.block_size)
        encrypted_data = f.read()

    passwd = getpass.getpass(prompt="Enter password (16 chars):")
    if len(passwd) > 16:
        passwd = passwd[:16]
        print("Password length greater than 16, truncated.")
    elif len(passwd) < 16:
        passwd += ' ' * (16 - len(passwd))
        print("Password length less than 16, filled with blanks.")
    passwd = bytes(passwd.encode('utf-8'))

    cipher = AES.new(passwd, AES.MODE_CBC, iv)
    decrypted_data = cipher.decrypt(encrypted_data)
    unpadded_data = decrypted_data[:-decrypted_data[-1]]

    return unpadded_data

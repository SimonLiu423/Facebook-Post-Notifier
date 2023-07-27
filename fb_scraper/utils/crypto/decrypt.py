from Crypto.Cipher import AES
import yaml
import getpass


def decrypt(encrypted_file):
    # read the encrypted file contents
    with open(encrypted_file, 'rb') as f:
        encrypted_data = f.read()

    # create the decryption key and initialization vector (IV)
    iv = encrypted_data[:AES.block_size]

    passwd = getpass.getpass(prompt="Enter password (16 chars):")
    if len(passwd) > 16:
        passwd = passwd[:16]
        print("Password length greater than 16, truncated.")
    elif len(passwd) < 16:
        passwd += ' ' * (16 - len(passwd))
        print("Password length less than 16, filled with blanks.")
    passwd = bytes(passwd.encode('utf-8'))

    # create the cipher object and decrypt the data
    cipher = AES.new(passwd, AES.MODE_CBC, iv)
    decrypted_data = cipher.decrypt(encrypted_data[AES.block_size:])

    return decrypted_data

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
import base64

class Encrypt:
    def encrypt_msg(message, public_key_path):
        recipient_key = RSA.import_key(open(public_key_path).read())
        cipher_rsa = PKCS1_OAEP.new(recipient_key)
        encrypted_message =  cipher_rsa.encrypt(message.encode())
        msg = base64.b64encode(encrypted_message)
        return msg
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

import secrets
import base64
import jwt
import os

CURR_DIR = os.path.dirname(os.path.abspath(__file__))

# RSA & hashing
def generate_rsa_key_pair():
    """
    Generate a new key pair in PEM format and store them locally. This method 
    is meant for development only. When in production, store your private key 
    in a secure location.
    """

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()


    private_key_pem = private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                                format=serialization.PrivateFormat.PKCS8,
                                                encryption_algorithm=serialization.NoEncryption())
    public_key_der = public_key.public_bytes(encoding=serialization.Encoding.DER,
                                        format=serialization.PublicFormat.SubjectPublicKeyInfo)
    

    with open(f'{CURR_DIR}/vault/public_key.pem', 'wb') as public_key_file:
        public_key_file.write(public_key_der)

    with open(f'{CURR_DIR}/vault/private_key.pem', 'wb') as private_key_file:
        private_key_file.write(private_key_pem)

def hash_plaintext(plaintext) -> bytes:
    """
    Hash plaintext using SHA256. Output is in hash.

    Note: SHA256 is a one-way hash function. It is not possible to decrypt the
    output to obtain the original plaintext. The only way to verify the
    plaintext is to hash it again and compare the hashes.
    """
    digest = hashes.Hash(hashes.SHA256())
    digest.update(plaintext.encode('utf-8'))
    hash = digest.finalize()

    return hash

def encrypt_rsa_plaintext(plaintext, public_key) -> str:
    """
    Hashes and encrypts a plaintext using the public key. Output is in ciphertext.
    """
    hashed_plaintext = hash_plaintext(plaintext)

    ciphertext = public_key.encrypt(
        hashed_plaintext, 
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    ciphertext = base64.b64encode(ciphertext).decode('utf-8')

    return ciphertext

def decrypt_rsa_ciphertext(ciphertext, private_key) -> str:
    """
    Decrypt ciphertext using the private key. Output is in plaintext.
    """
    ciphertext = base64.b64decode(ciphertext)

    decryption = private_key.decrypt(
        ciphertext, 
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    decryption = base64.b64encode(decryption).decode('utf-8')

    return decryption


# JWT
def generate_jwt(payload):
    """
    Generates a JWT token using the payload and the secret signature.
    """
    ############ DEVELOPMENT ONLY ############
    with open(f'{CURR_DIR}/vault/jwt_private_key.pem', 'rb') as private_key_file:
        private_key = serialization.load_pem_private_key(
            private_key_file.read(),
            password=None,
            backend=None,
        )
    ############ DEVELOPMENT ONLY ############

    return jwt.encode(payload, private_key, algorithm='RS256')

def decode_jwt(cookie):
    """
    Decodes a JWT token using the secret signature.
    """
    ############ DEVELOPMENT ONLY ############
    with open(f'{CURR_DIR}/vault/jwt_public_key.pem', 'rb') as public_key_file:
        public_key = serialization.load_der_public_key(
            public_key_file.read()
            , backend=None
        )
    ############ DEVELOPMENT ONLY ############

    return jwt.decode(cookie, public_key, algorithms=['RS256'])


# Methods & exceptions
def generate_session_token(length=64):
    """
    Generates a random key for general use.
    """
    return secrets.token_hex(length//2)

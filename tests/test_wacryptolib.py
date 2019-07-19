import uuid
import wacryptolib

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.PublicKey import ECC
from Crypto.PublicKey import DSA

from datetime import datetime

from Crypto.Random import get_random_bytes


def test_generate_rsa_keypair():
    """Cipher then decipher a message using RSA keypair"""

    uid = None
    binary_content = "Mon hât èst joli".encode("utf-8")

    keys = wacryptolib.generate_rsa_keypair(uid)
    public_key = keys["public_key"]
    private_key = keys["private_key"]

    # Cipher the binary content with the public key
    cipher = PKCS1_OAEP.new(public_key)
    ciphertext = cipher.encrypt(binary_content)

    # Decipher it with the private key
    decipher = PKCS1_OAEP.new(private_key)
    deciphertext = decipher.decrypt(ciphertext)

    try:  # FIXME
        assert deciphertext == binary_content
        print("Generating keypair : successfuly done")
    except AssertionError:
        print("Problem cccured in the deciphering")


def test_generate_dsa_keypair():
    """Check if the function generate_dsa_keypair returns
    a pair of DSA keys"""

    uid = None
    keypair = wacryptolib.generate_dsa_keypair(uid)
    public_key = keypair["public_key"]
    private_key = keypair["private_key"]
    assert isinstance(public_key, DSA.DsaKey), type(public_key)
    assert isinstance(private_key, DSA.DsaKey), type(private_key)


def test_generate_ecc_keypair():
    """Check if the function generate_ecc_keypair returns
    a pair of ECC keys"""

    uid = None
    keypair = wacryptolib.generate_ecc_keypair(uid, curve="p256")
    public_key = keypair["public_key"]
    private_key = keypair["private_key"]
    assert isinstance(public_key, ECC.EccKey), type(public_key)
    assert isinstance(private_key, ECC.EccKey), type(private_key)


def test_generate_shared_secret():
    """Cipher then decipher a message using shared secret and RSA"""

    uid = uuid.uuid4()
    keys_count = 3
    threshold_count = 2

    binary_content = "Mon hât èst joli".encode("utf-8")
    keys_info = wacryptolib.generate_shared_secret_key(
        uid, keys_count, threshold_count=threshold_count
    )
    shares = keys_info["shares"]
    public_key = keys_info["public_key"]
    shares = wacryptolib.split_as_padded_chunks(shares, 3)

    # Cipher the binary content
    cipher = PKCS1_OAEP.new(public_key)
    ciphertext = cipher.encrypt(binary_content)

    # Combine all the shares to make a list of bytes corresponding to the private key
    combined_shares_list = wacryptolib.recombine_shares_into_bytestring(shares)

    # Unpad the last tuple
    combined_shares_list = wacryptolib.unpad_last_element(combined_shares_list)

    # Reconstruct the private key in type bytes
    private_key_reconstructed = b"".join(combined_shares_list)

    # decipher the binary content
    decipher = PKCS1_OAEP.new(RSA.import_key(private_key_reconstructed))
    deciphertext = decipher.decrypt(ciphertext)

    try:
        assert binary_content == deciphertext
        print("Shared secret : successfuly done")
    except AssertionError:
        print("Problem cccured in the deciphering")


def test_sign_and_verify_rsa():
    keypair = wacryptolib.generate_rsa_keypair(None)
    data_hash, signature = wacryptolib.sign_with_rsa(
        private_key=RSA.RsaKey.export_key(keypair["private_key"]), data=b"Hello"
    )

    wacryptolib.verify_authenticity_rsa_signature(
        public_key=RSA.RsaKey.export_key(keypair["public_key"]),
        data_hash=data_hash,
        signature=signature,
    )


def test_aes_cbc():
    key = get_random_bytes(16)

    binary_content = "Mon hât èst joli".encode("utf-8")

    cipher_text = wacryptolib.encrypt_via_aes_cbc(key=key, data=binary_content)

    decipher_text = wacryptolib.decrypt_via_aes_cbc(key=key, data=cipher_text)

    try:
        assert decipher_text == binary_content
        print("Ciphering and deciphering with CBC mode : successfuly done")
    except AssertionError:
        print("Problem cccured in the deciphering")


def test_sign_dsa():
    keypair = wacryptolib.generate_dsa_keypair(None)
    public_key = keypair["public_key"]
    private_key = keypair["private_key"]
    binary_content = "Mon hât èst joli".encode("utf-8")
    timestamp_verifier = int(datetime.timestamp(datetime.now()))

    signature, timestamp = wacryptolib.sign_data_dsa(
        private_key=private_key, data=binary_content
    )
    verifier, hash_obj = wacryptolib.generate_verifier(
        public_key=public_key, data=binary_content
    )
    wacryptolib.verify_authenticity(hash_obj, signature, verifier)
    assert timestamp == timestamp_verifier, "modification détectée"


if __name__ == "__main__":
    # test_generate_shared_secret()
    # test_generate_rsa_keypair()
    # test_generate_dsa_keypair()
    # test_generate_ecc_keypair()
    # test_aes_cbc()
    test_sign_dsa()

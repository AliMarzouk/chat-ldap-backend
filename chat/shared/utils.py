import os

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives.serialization import (Encoding, PrivateFormat, NoEncryption, PublicFormat)

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
import datetime
import uuid

from chat.shared.global_settings import ca_key_path, ca_path, private_key_path, public_key_path, crt_path
from myChannelTuto.settings import BASE_DIR


def generate_request(common_name, country_name, state, loc_name, private_key=None):
    if private_key is None:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
    builder = x509.CertificateSigningRequestBuilder()
    builder = builder.subject_name(x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        x509.NameAttribute(NameOID.COUNTRY_NAME, country_name),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state),
        x509.NameAttribute(NameOID.LOCALITY_NAME, loc_name),
    ]))
    builder = builder.add_extension(
        x509.BasicConstraints(ca=False, path_length=None), critical=True,
    )

    request = builder.sign(
        private_key, hashes.SHA256(), default_backend()
    )

    csr = request.public_bytes(Encoding.PEM)
    key_pem = private_key.private_bytes(Encoding.PEM,
                                        PrivateFormat.TraditionalOpenSSL,
                                        NoEncryption())

    return csr, key_pem


class Certification:
    def __init__(self):
        self.ca = x509.load_pem_x509_certificate(open(ca_path, 'rb').read(), default_backend())
        self.ca_key = serialization.load_pem_private_key(open(ca_key_path, 'rb').read(), password=None,
                                                         backend=default_backend())
        self.pem_ca_pb_key = self.ca_key.public_key().public_bytes(Encoding.PEM, PublicFormat.PKCS1)
        self.ca_pb_key = serialization.load_pem_public_key(self.pem_ca_pb_key, backend=default_backend())

    def generate_certificate(self, pem_csr):
        csr = x509.load_pem_x509_csr(pem_csr, default_backend())
        builder = x509.CertificateBuilder()
        builder = builder.subject_name(csr.subject)
        builder = builder.issuer_name(self.ca.subject)
        builder = builder.not_valid_before(datetime.datetime.now())
        builder = builder.not_valid_after(datetime.datetime.now() +
                                          datetime.timedelta(7))  # 7 days
        builder = builder.public_key(csr.public_key())
        builder = builder.serial_number(int(uuid.uuid4()))
        for ext in csr.extensions:
            builder = builder.add_extension(ext.value, ext.critical)

        certificate = builder.sign(
            private_key=self.ca_key,
            algorithm=hashes.SHA256(),
            backend=default_backend()
        )

        client_crt = certificate.public_bytes(serialization.Encoding.PEM)

        return client_crt

    # a :class:`~cryptography.exceptions.InvalidSignature`
    # exception will be raised if the signature fails to verify.
    def verify_certificate(self, pem_cert):
        cert_to_check = x509.load_pem_x509_certificate(pem_cert)
        self.ca_pb_key.verify(
            cert_to_check.signature,
            cert_to_check.tbs_certificate_bytes,
            padding.PKCS1v15(),
            cert_to_check.signature_hash_algorithm,
        )


def encrypt_from_pem_crt(pem_crt, message):
    crt = x509.load_pem_x509_certificate(pem_crt, default_backend())
    pb_key = crt.public_key()
    ciphertext = Rsa_Service.encrypt(message, pb_key)
    return ciphertext


class RsaUtils:
    def __init__(self):
        pb = open(public_key_path, 'rb').read()
        key = open(private_key_path, 'rb').read()
        self.public_key = serialization.load_pem_public_key(pb, backend=default_backend())
        self.private_key = serialization.load_pem_private_key(key, password=None, backend=default_backend())
        try:
            self.crt = self.get_certificate()
        except:
            self.crt = self.generate_certificate('Server Chat', 'TN', 'Tunis', 'Tunis')

    def generate_keys(self):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()

        with open(private_key_path, 'wb') as f:
            f.write(self.private_key.private_bytes(Encoding.PEM,
                                                   PrivateFormat.TraditionalOpenSSL,
                                                   NoEncryption()))
        with open(public_key_path, 'wb') as f:
            f.write(self.public_key.public_bytes(Encoding.PEM, format=PublicFormat.PKCS1))

    def encrypt(self, message, pb_key=None):
        print(message)
        if pb_key is None:
            pb_key = self.public_key
        ciphertext = pb_key.encrypt(
            message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return ciphertext

    def decrypt(self, ciphertext, private_key=None):
        if private_key is None:
            private_key = self.private_key
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext

    def generate_certificate(self, common_name, country_name, state, loc_name):
        csr, key = generate_request(common_name, country_name, state, loc_name, self.private_key)
        crt = Certificate_Server.generate_certificate(csr)
        with open(crt_path, 'wb') as f:
            f.write(crt)
        return crt

    def get_certificate(self):
        crt = open(crt_path, 'r').read()
        return crt


Certificate_Server: Certification = Certification()
Rsa_Service = RsaUtils()

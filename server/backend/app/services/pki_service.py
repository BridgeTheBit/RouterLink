import datetime
import os
from pathlib import Path
from typing import Tuple
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec, x25519
from app.config import settings


class PKIService:
    """Manages PKI Certificates for OpenVPN and Keypairs for WireGuard."""

    @classmethod
    def get_ca_paths(cls) -> Tuple[Path, Path]:
        ca_cert_path = settings.CERTS_DIR / "ca.crt"
        ca_key_path = settings.CERTS_DIR / "ca.key"
        return ca_cert_path, ca_key_path

    @classmethod
    def get_server_paths(cls) -> Tuple[Path, Path]:
        server_cert_path = settings.CERTS_DIR / "server.crt"
        server_key_path = settings.CERTS_DIR / "server.key"
        return server_cert_path, server_key_path

    @classmethod
    def ensure_pki(cls) -> None:
        """Ensures Root CA and Server certificates exist, generating them if not."""
        ca_cert_path, ca_key_path = cls.get_ca_paths()
        server_cert_path, server_key_path = cls.get_server_paths()

        if not ca_cert_path.exists() or not ca_key_path.exists():
            cls._generate_ca(ca_cert_path, ca_key_path)

        if not server_cert_path.exists() or not server_key_path.exists():
            cls._generate_server_cert(ca_cert_path, ca_key_path, server_cert_path, server_key_path)

    @classmethod
    def _generate_ca(cls, cert_path: Path, key_path: Path) -> None:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        subject = issuer = x509.Name([
            x509.NameAttribute(x509.NameOID.COMMON_NAME, "RouterLink-CA"),
            x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, "RouterLink Ecosystem"),
        ])
        now = datetime.datetime.now(datetime.timezone.utc)
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - datetime.timedelta(days=1))
            .not_valid_after(now + datetime.timedelta(days=3650)) # 10 years
            .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
            .sign(private_key, hashes.SHA256(), default_backend())
        )

        with open(key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))

        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

    @classmethod
    def _generate_server_cert(cls, ca_cert_path: Path, ca_key_path: Path, cert_path: Path, key_path: Path) -> None:
        with open(ca_key_path, "rb") as f:
            ca_key = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())
        with open(ca_cert_path, "rb") as f:
            ca_cert = x509.load_pem_x509_certificate(f.read(), backend=default_backend())

        server_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        subject = x509.Name([
            x509.NameAttribute(x509.NameOID.COMMON_NAME, "RouterLink-Server"),
            x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, "RouterLink Ecosystem"),
        ])
        now = datetime.datetime.now(datetime.timezone.utc)
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(ca_cert.subject)
            .public_key(server_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - datetime.timedelta(days=1))
            .not_valid_after(now + datetime.timedelta(days=1825)) # 5 years
            .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
            .add_extension(
                x509.ExtendedKeyUsage([x509.ExtendedKeyUsageOID.SERVER_AUTH]),
                critical=False
            )
            .sign(ca_key, hashes.SHA256(), default_backend())
        )

        with open(key_path, "wb") as f:
            f.write(server_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))

        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

    @classmethod
    def generate_wireguard_keypair(cls) -> Tuple[str, str]:
        """Generates standard Curve25519 base64 private and public keys for WireGuard."""
        private_key = x25519.X25519PrivateKey.generate()
        public_key = private_key.public_key()

        import base64
        priv_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        pub_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )

        return base64.b64encode(priv_bytes).decode("ascii"), base64.b64encode(pub_bytes).decode("ascii")

    @classmethod
    def get_ca_cert_content(cls) -> str:
        ca_cert_path, _ = cls.get_ca_paths()
        cls.ensure_pki()
        return ca_cert_path.read_text(encoding="utf-8")


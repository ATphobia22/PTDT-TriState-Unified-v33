from __future__ import annotations

import ipaddress
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID


def _write_private_key(path: Path, key: rsa.RSAPrivateKey) -> None:
    path.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    os.chmod(path, 0o600)


def _sign_certificate(
    *, subject: x509.Name, issuer: x509.Name, public_key, issuer_key, serial: int,
    is_ca: bool, eku: x509.ObjectIdentifier | None, san: list[x509.GeneralName], now: datetime
) -> x509.Certificate:
    builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(public_key)
        .serial_number(serial)
        .not_valid_before(now - timedelta(minutes=5))
        .not_valid_after(now + timedelta(days=365))
        .add_extension(x509.BasicConstraints(ca=is_ca, path_length=1 if is_ca else None), critical=True)
        .add_extension(x509.SubjectAlternativeName(san), critical=False)
    )
    if eku is not None:
        builder = builder.add_extension(x509.ExtendedKeyUsage([eku]), critical=False)
    return builder.sign(issuer_key, hashes.SHA256())


def provision_internal_tls_certs(target_dir: str = "build/certs") -> None:
    directory = Path(target_dir)
    directory.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)

    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    ca_subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "PTDT Internal Root CA")])
    ca_cert = _sign_certificate(
        subject=ca_subject, issuer=ca_subject, public_key=ca_key.public_key(), issuer_key=ca_key,
        serial=x509.random_serial_number(), is_ca=True, eku=None, san=[], now=now,
    )

    server_key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    server_subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "ptdt-gateway.internal")])
    server_cert = _sign_certificate(
        subject=server_subject, issuer=ca_subject, public_key=server_key.public_key(), issuer_key=ca_key,
        serial=x509.random_serial_number(), is_ca=False, eku=ExtendedKeyUsageOID.SERVER_AUTH,
        san=[x509.DNSName("localhost"), x509.DNSName("ptdt-gateway"), x509.DNSName("ptdt-gateway.internal"), x509.IPAddress(ipaddress.ip_address("127.0.0.1"))], now=now,
    )

    client_key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    client_subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "ptdt-engineering-node")])
    client_cert = _sign_certificate(
        subject=client_subject, issuer=ca_subject, public_key=client_key.public_key(), issuer_key=ca_key,
        serial=x509.random_serial_number(), is_ca=False, eku=ExtendedKeyUsageOID.CLIENT_AUTH,
        san=[x509.DNSName("ptdt-engineering-node")], now=now,
    )

    _write_private_key(directory / "root_ca.key", ca_key)
    _write_private_key(directory / "server.key", server_key)
    _write_private_key(directory / "client.key", client_key)
    (directory / "root_ca.crt").write_bytes(ca_cert.public_bytes(serialization.Encoding.PEM))
    (directory / "server.crt").write_bytes(server_cert.public_bytes(serialization.Encoding.PEM))
    (directory / "client.crt").write_bytes(client_cert.public_bytes(serialization.Encoding.PEM))


if __name__ == "__main__":
    provision_internal_tls_certs()

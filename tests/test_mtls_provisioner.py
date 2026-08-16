from cryptography import x509
from cryptography.x509.oid import ExtendedKeyUsageOID

from security.cert_provisioner import provision_internal_tls_certs


def _load(path):
    return x509.load_pem_x509_certificate(path.read_bytes())


def test_provisioned_server_and_client_have_distinct_usage(tmp_path):
    provision_internal_tls_certs(str(tmp_path))
    server = _load(tmp_path / "server.crt")
    client = _load(tmp_path / "client.crt")
    server_eku = server.extensions.get_extension_for_class(x509.ExtendedKeyUsage).value
    client_eku = client.extensions.get_extension_for_class(x509.ExtendedKeyUsage).value
    assert ExtendedKeyUsageOID.SERVER_AUTH in server_eku
    assert ExtendedKeyUsageOID.CLIENT_AUTH in client_eku
    assert server.issuer == client.issuer
    assert server.subject != client.subject

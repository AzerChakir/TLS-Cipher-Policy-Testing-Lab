import socket
import ssl
import threading
import unittest
from unittest import mock

from server import (
    TLS12_CIPHERS,
    TLS13_CIPHERS,
    create_server,
    create_ssl_context,
    parse_args,
)


class TLSPolicyTests(unittest.TestCase):
    def test_command_line_defaults(self):
        with mock.patch("sys.argv", ["server.py"]):
            args = parse_args()

        self.assertEqual(args.host, "127.0.0.1")
        self.assertEqual(args.port, 8443)

    def test_context_allows_only_declared_strong_ciphers(self):
        names = {cipher["name"] for cipher in create_ssl_context().get_ciphers()}

        self.assertEqual(
            names,
            set(TLS12_CIPHERS) | set(TLS13_CIPHERS),
        )

    def test_strongest_tls12_cipher_is_preferred(self):
        server = create_server(port=0)
        thread = threading.Thread(target=server.handle_request, daemon=True)
        thread.start()

        client_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        client_context.minimum_version = ssl.TLSVersion.TLSv1_2
        client_context.maximum_version = ssl.TLSVersion.TLSv1_2
        client_context.set_ciphers(":".join(TLS12_CIPHERS))
        client_context.check_hostname = False
        client_context.verify_mode = ssl.CERT_NONE

        with socket.create_connection(server.server_address) as connection:
            with client_context.wrap_socket(
                connection,
                server_hostname="localhost",
            ) as tls_connection:
                self.assertEqual(tls_connection.cipher()[0], TLS12_CIPHERS[0])

        thread.join(timeout=2)
        server.server_close()
        self.assertFalse(thread.is_alive())

    def test_tls13_cipher_order_starts_with_strongest_suite(self):
        names = [
            cipher["name"]
            for cipher in create_ssl_context().get_ciphers()
            if cipher["protocol"] == "TLSv1.3"
        ]

        self.assertEqual(names, list(TLS13_CIPHERS))


if __name__ == "__main__":
    unittest.main()

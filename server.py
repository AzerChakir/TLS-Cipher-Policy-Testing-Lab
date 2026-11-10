import argparse
import http.server
from functools import partial
from pathlib import Path
import ssl

HOST = "127.0.0.1"
PORT = 8443
BASE_DIR = Path(__file__).resolve().parent
CERT_FILE = BASE_DIR / "server.crt"
KEY_FILE = BASE_DIR / "server.key"
PUBLIC_DIR = BASE_DIR / "public"

TLS13_CIPHERS = (
    "TLS_AES_256_GCM_SHA384",
    "TLS_CHACHA20_POLY1305_SHA256",
    "TLS_AES_128_GCM_SHA256",
)
TLS12_CIPHERS = (
    "ECDHE-RSA-AES256-GCM-SHA384",
    "ECDHE-RSA-CHACHA20-POLY1305",
    "ECDHE-RSA-AES128-GCM-SHA256",
)


def create_ssl_context(
    cert_file: Path = CERT_FILE,
    key_file: Path = KEY_FILE,
) -> ssl.SSLContext:
    """Create the server TLS context with the lab's explicit cipher policy."""
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.maximum_version = ssl.TLSVersion.MAXIMUM_SUPPORTED
    context.set_ciphers(":".join(TLS12_CIPHERS))
    context.options |= ssl.OP_CIPHER_SERVER_PREFERENCE
    context.load_cert_chain(certfile=cert_file, keyfile=key_file)
    return context


def create_server(
    host: str = HOST,
    port: int = PORT,
    cert_file: Path = CERT_FILE,
    key_file: Path = KEY_FILE,
) -> http.server.HTTPServer:
    server = http.server.HTTPServer(
        (host, port),
        partial(
            http.server.SimpleHTTPRequestHandler,
            directory=str(PUBLIC_DIR),
        ),
    )
    server.socket = create_ssl_context(
        cert_file=cert_file,
        key_file=key_file,
    ).wrap_socket(
        server.socket,
        server_side=True,
    )
    return server


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the local HTTPS TLS cipher-policy test server."
    )
    parser.add_argument(
        "--host",
        default=HOST,
        help=f"Address to bind to (default: {HOST})",
    )
    parser.add_argument(
        "--port",
        default=PORT,
        type=int,
        help=f"TCP port to bind to (default: {PORT})",
    )
    parser.add_argument(
        "--certfile",
        default=CERT_FILE,
        type=Path,
        help=f"PEM certificate path (default: {CERT_FILE.name})",
    )
    parser.add_argument(
        "--keyfile",
        default=KEY_FILE,
        type=Path,
        help=f"PEM private-key path (default: {KEY_FILE.name})",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    server = create_server(
        host=args.host,
        port=args.port,
        cert_file=args.certfile,
        key_file=args.keyfile,
    )
    print(f"HTTPS server running at https://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
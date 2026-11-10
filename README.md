# TLS Cipher-Policy Testing Lab

Small, dependency-free Python HTTPS server for verifying that weak TLS
protocols and cipher suites are disabled. The project combines an explicit
Python `ssl` policy with automated handshake tests and the linked
[`testssl.sh`](./testssl.sh/) benchmark.

> **Scope:** This is an educational and validation tool, not a production
> web server. Do not expose it to the public Internet.

## What it enforces

The server allows TLS 1.2 and TLS 1.3 only. It enables these AEAD cipher
suites:

| Protocol | Cipher suites, in preferred order |
| --- | --- |
| TLS 1.3 | `TLS_AES_256_GCM_SHA384`, `TLS_CHACHA20_POLY1305_SHA256`, `TLS_AES_128_GCM_SHA256` |
| TLS 1.2 | `ECDHE-RSA-AES256-GCM-SHA384`, `ECDHE-RSA-CHACHA20-POLY1305`, `ECDHE-RSA-AES128-GCM-SHA256` |

All TLS 1.2 suites provide forward secrecy through ECDHE. TLS 1.3 cipher
ordering is reported by the OpenSSL runtime; Python's standard `ssl` API does
not expose OpenSSL's TLS 1.3 cipher-order configuration function. The policy
still restricts TLS 1.3 to strong AEAD suites.

The server explicitly enables `OP_CIPHER_SERVER_PREFERENCE` for TLS 1.2, so
the server selects the first allowed suite when the client offers multiple
allowed suites.

## Requirements

- Python 3.10 or newer
- OpenSSL 1.1.1 or newer
- `openssl` command-line tool
- `testssl.sh` prerequisites if you want to run the benchmark

No third-party Python packages are required.

## Quick start

Clone the repository and enter it:

```sh
git clone https://github.com/AzerChakir/POLICY-BASED-TLS-TESTING-TOOL.git
cd POLICY-BASED-TLS-TESTING-TOOL
git submodule update --init --recursive
```

Generate a local self-signed certificate:

```sh
./generate_cert.sh
```

Start the server:

```sh
python3 server.py
```

Open <https://127.0.0.1:8443/> in a browser. A certificate warning is expected
because the certificate is self-signed. For a command-line request:

```sh
curl --insecure https://127.0.0.1:8443/
```

The server serves only files from `public/`; private keys and test files are
not exposed over HTTP.

Stop the server with `Ctrl-C`.

The bind address, port, and certificate files can be changed without editing
the source:

```sh
python3 server.py \
  --host 127.0.0.1 \
  --port 9443 \
  --certfile server.crt \
  --keyfile server.key
```

Use `python3 server.py --help` to see all options.

## Run the tests

The unit tests inspect the configured cipher allow-list and perform a real
TLS 1.2 handshake to verify server-side cipher preference:

```sh
python3 -m unittest -v test_tls_policy.py
```

The test server uses an ephemeral port, so tests do not require port 8443 to
be available.

## Benchmark with testssl.sh

With the server running in one terminal, run this from another:

```sh
./testssl.sh/testssl.sh \
  --protocols \
  --cipher-per-proto \
  --server-preference \
  --warnings batch \
  127.0.0.1:8443
```

Expected results:

- SSLv2, SSLv3, TLS 1.0, and TLS 1.1 are not offered.
- TLS 1.2 and TLS 1.3 are offered.
- Only the six suites listed above are detected.
- `TLS_AES_256_GCM_SHA384` and
  `ECDHE-RSA-AES256-GCM-SHA384` appear first in their respective lists.
- Server cipher order is reported as enabled.

The `testssl.sh` directory is a Git submodule used only as a benchmark tool
for this project; it is not part of the Python server implementation. Clone
with `--recurse-submodules`, or run `git submodule update --init --recursive`
after cloning.

## Project layout

```text
server.py              HTTPS server and TLS policy
test_tls_policy.py     Automated TLS policy tests
generate_cert.sh       Local self-signed certificate generator
public/                Files intentionally served by the HTTPS server
testssl.sh/            Benchmark tool used to assess the server
```

## Security notes

- Never commit `server.key`, production certificates, or real credentials.
  They are ignored by `.gitignore`.
- The generated certificate is self-signed and suitable only for local
  testing.
- `http.server` is not hardened for production workloads.
- Binding to `127.0.0.1` keeps the default service local to the machine.
- `--insecure`/browser bypasses disable certificate verification and should
  only be used for this local self-signed certificate.
- Cipher strength is only one part of TLS security; certificate validation,
  key management, protocol configuration, patching, and HTTP hardening also
  matter.

## Possible future improvements

- Add CI for the Python unit tests.
- Add a trusted local CA workflow so browser testing does not require a
  certificate bypass.
- Add tests for certificate-file errors and invalid command-line values.

## Contributing

Keep changes focused, document security-impacting behavior, and run the unit
tests before submitting a pull request. Changes to the TLS policy should also
include updated scanner expectations and a short security rationale.

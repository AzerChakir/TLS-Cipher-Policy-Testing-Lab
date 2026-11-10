#!/usr/bin/env sh
set -eu

openssl req -x509 -newkey rsa:3072 -sha256 -nodes \
  -keyout server.key \
  -out server.crt \
  -days 365 \
  -subj "/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"

chmod 600 server.key
printf '%s\n' "Generated server.crt and server.key"

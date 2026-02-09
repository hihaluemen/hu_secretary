#!/usr/bin/env sh
set -eu

mkdir -p /etc/nginx/certs

if [ ! -f /etc/nginx/certs/selfsigned.crt ] || [ ! -f /etc/nginx/certs/selfsigned.key ]; then
  openssl req -x509 -nodes -newkey rsa:2048 -days 3650 \
    -keyout /etc/nginx/certs/selfsigned.key \
    -out /etc/nginx/certs/selfsigned.crt \
    -subj "/C=CN/ST=Beijing/L=Beijing/O=MiShu/OU=Demo/CN=localhost" >/dev/null 2>&1
fi

exec nginx -g 'daemon off;'

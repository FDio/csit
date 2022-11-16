#!/usr/bin/env bash

mkdir -p ./nginx/ssl
cd ./nginx/ssl

FILE_NAME="subdomains.amazonaws.com"

openssl genrsa -des3 -out CA.key 2048

openssl req -x509 -new -nodes -key CA.key -sha256 -days 8000 -out CA.pem

openssl x509 -in CA.pem -inform PEM -out CA.crt

openssl genrsa -out $FILE_NAME.key 2048
openssl req -new -key $FILE_NAME.key -out $FILE_NAME.csr

cat > $FILE_NAME.ext << EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names
[alt_names]
DNS.1 = *.amazonaws.com
DNS.2 = *.us-east-1.amazonaws.com
DNS.3 = *.s3.amazonaws.com
EOF

openssl x509 -req -in $FILE_NAME.csr -CA CA.pem -CAkey CA.key -CAcreateserial \
-out $FILE_NAME.crt -days 8000 -sha256 -extfile $FILE_NAME.ext
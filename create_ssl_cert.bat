@echo off
echo Generating SSL certificate for development...

:: Create directory for certificates if it doesn't exist
if not exist certificates mkdir certificates

:: Generate private key and certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 ^
    -keyout certificates/dev-key.pem ^
    -out certificates/dev-cert.pem ^
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

echo.
echo SSL Certificate created at:
echo - certificates/dev-key.pem (private key)
echo - certificates/dev-cert.pem (certificate)
echo.
echo Note: This is a self-signed certificate for development only.
echo For production, use a certificate from a trusted CA.
pause 
"""
Generate self-signed SSL certificate for local testing.
"""
import os
import subprocess
import sys
from pathlib import Path

# Ensure the ssl directory exists
ssl_dir = Path('ssl')
ssl_dir.mkdir(exist_ok=True)

# Certificate file paths
key_file = ssl_dir / 'localhost.key'
cert_file = ssl_dir / 'localhost.crt'

def generate_certificate():
    """Generate a self-signed SSL certificate for local development."""
    print("Generating self-signed SSL certificate for local development...")

    if key_file.exists() and cert_file.exists():
        print("Certificate files already exist.")
        overwrite = input("Do you want to regenerate them? (y/n): ").lower() == 'y'
        if not overwrite:
            print("Using existing certificate files.")
            return

    # Using OpenSSL to generate self-signed certificates
    try:
        # Generate private key
        subprocess.run([
            'openssl', 'genrsa',
            '-out', str(key_file),
            '2048'
        ], check=True)
        
        # Generate certificate
        subprocess.run([
            'openssl', 'req', '-new',
            '-key', str(key_file),
            '-out', str(ssl_dir / 'localhost.csr'),
            '-subj', '/CN=localhost/O=LocalDevelopment/C=US'
        ], check=True)
        
        # Sign certificate
        subprocess.run([
            'openssl', 'x509', '-req',
            '-days', '365',
            '-in', str(ssl_dir / 'localhost.csr'),
            '-signkey', str(key_file),
            '-out', str(cert_file)
        ], check=True)
        
        print(f"SSL certificate generated successfully:")
        print(f"  - Key file: {key_file}")
        print(f"  - Certificate file: {cert_file}")
        print("\nIMPORTANT: This is a self-signed certificate for development purposes only.")
        print("You'll need to add this certificate to your browser's trusted certificates.")
        
    except subprocess.CalledProcessError as e:
        print(f"Error generating SSL certificate: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("OpenSSL not found. Please install OpenSSL to generate SSL certificates.")
        print("On Windows: You can download from https://slproweb.com/products/Win32OpenSSL.html")
        print("On macOS: Run 'brew install openssl'")
        print("On Linux: Run 'apt-get install openssl' or equivalent for your distribution")
        sys.exit(1)

def run_server_with_ssl():
    """Print instructions for running the Django server with SSL."""
    print("\nTo run the Django development server with SSL, use the following command:")
    print(f"python manage.py runserver_plus --cert-file={cert_file} --key-file={key_file}")
    print("\nYou may need to install django-extensions first:")
    print("pip install django-extensions")
    print("\nAlternatively, you can use the daphne ASGI server directly:")
    print(f"daphne -e ssl:8000:privateKey={key_file}:certKey={cert_file} ecommerce.asgi:application")

if __name__ == '__main__':
    generate_certificate()
    run_server_with_ssl() 
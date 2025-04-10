from datetime import timedelta, timezone, datetime
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.hazmat.primitives.serialization import PublicFormat
from cryptography.hazmat.backends import default_backend
import base64
from getpass import getpass
import hashlib
import jwt

account = "vyb82036"

def get_private_key_passphrase():
    return getpass('Passphrase for private key: ')

# Private key that you will load from the private key file.
private_key = None

# Open the private key file.
# Replace <private_key_file_path> with the path to your private key file (e.g. /x/y/z/rsa_key.p8).
with open('C://Users//User//Documents//snowsql//rsa_key.p8', 'rb') as pem_in:
    pemlines = pem_in.read()
    try:
        # Try to access the private key without a passphrase.
        private_key = load_pem_private_key(pemlines, None, default_backend())
    except TypeError:
        # If that fails, provide the passphrase returned from get_private_key_passphrase().
        private_key = load_pem_private_key(pemlines, get_private_key_passphrase().encode(), default_backend())

# Get the raw bytes of the public key.
public_key_raw = private_key.public_key().public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)

# Get the sha256 hash of the raw bytes.
sha256hash = hashlib.sha256()
sha256hash.update(public_key_raw)

# Base64-encode the value and prepend the prefix 'SHA256:'.
public_key_fp = 'SHA256:' + base64.b64encode(sha256hash.digest()).decode('utf-8')


# Get the account identifier without the region, cloud provider, or subdomain.
if not '.global' in account:
    idx = account.find('.')
    if idx > 0:
        account = account[0:idx]
    else:
        # Handle the replication case.
        idx = account.find('-')
        if idx > 0:
            account = account[0:idx]

# Use uppercase for the account identifier and user name.
account = account.upper()
user = "CORTEXSA".upper()
qualified_username = account + "." + user

# Get the current time in order to specify the time when the JWT was issued and the expiration time of the JWT.
now = datetime.now(timezone.utc)

# Specify the length of time during which the JWT will be valid. You can specify at most 1 hour.
lifetime = timedelta(minutes=59)

# Create the payload for the token.
payload = {

    # Set the issuer to the fully qualified username concatenated with the public key fingerprint (calculated in the  previous step).
    "iss": qualified_username + '.' + public_key_fp,

    # Set the subject to the fully qualified username.
    "sub": qualified_username,

    # Set the issue time to now.
    "iat": now,

    # Set the expiration time, based on the lifetime specified for this object.
    "exp": now + lifetime
}

# Generate the JWT. private_key is the private key that you read from the private key file in the previous step when you generated the public key fingerprint.
encoding_algorithm="RS256"
token = jwt.encode(payload, key=private_key, algorithm=encoding_algorithm)

if isinstance(token, bytes):
  token = token.decode('utf-8')
print("Generated JWT token:")
print(token)

# import datetime
# print(datetime.datetime.utcfromtimestamp(1727177203))
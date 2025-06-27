
import jwt
from cryptography.hazmat.primitives.asymmetric import ed25519
import time

def generate_ed25519_key_pair():
    """Generates an Ed25519 key pair."""
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key

def generate_jwt(private_key, tenant_id, user_id):
    """Generates a JWT signed with an Ed25519 private key."""
    payload = {
        'iss': 'IG-Shop-Agent',
        'sub': user_id,
        'aud': 'https://api.ig-shop-agent.com',
        'exp': int(time.time()) + 3600,  # 1 hour expiration
        'iat': int(time.time()),
        'tenant_id': tenant_id
    }
    encoded_jwt = jwt.encode(payload, private_key, algorithm='EdDSA')
    return encoded_jwt

def verify_jwt(encoded_jwt, public_key):
    """Verifies a JWT signed with an Ed25519 public key."""
    try:
        decoded_jwt = jwt.decode(encoded_jwt, public_key, algorithms=['EdDSA'])
        return decoded_jwt
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token")
        return None

if __name__ == '__main__':
    # Generate a key pair for a tenant
    tenant_private_key, tenant_public_key = generate_ed25519_key_pair()

    # Generate a JWT for a user in that tenant
    tenant_id = 'tenant-123'
    user_id = 'user-456'
    jwt_token = generate_jwt(tenant_private_key, tenant_id, user_id)
    print(f"Generated JWT: {jwt_token}")

    # Verify the JWT
    decoded_token = verify_jwt(jwt_token, tenant_public_key)
    if decoded_token:
        print(f"Decoded JWT: {decoded_token}")

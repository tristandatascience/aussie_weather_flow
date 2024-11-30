import os
import json
from hashlib import sha256
from datetime import datetime, timedelta
from fastapi import HTTPException
import jwt
from dotenv import load_dotenv
import os
# Load environment variables
load_dotenv()

# Retrieve the secret key from the environment
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set.")

ALGORITHM = "HS256"
USERS_PATH = os.getenv("USERS_PATH")
JSON_FILE_PATH = os.path.expanduser(USERS_PATH)

# Load users from a JSON file
def load_users():
    if os.path.exists(JSON_FILE_PATH):
        with open(JSON_FILE_PATH, "r") as file:
            users_data = json.load(file)
        return {user['username']: user for user in users_data}
    else:
        raise FileNotFoundError(f"Users file not found at {JSON_FILE_PATH}")

users_db = load_users()

# Verify the password
def verify_password(plain_password, hashed_password):
    return sha256(plain_password.encode()).hexdigest() == hashed_password

# Create an access token JWT
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    try:
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token generation failed: {e}")

# Extract the current user from the token
def get_current_user(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username or username not in users_db:
            raise HTTPException(status_code=401, detail="User not found")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token")

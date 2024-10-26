# auth.py
from fastapi import APIRouter, HTTPException, Depends, Request, Header
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials
from dotenv import load_dotenv
import os

router = APIRouter(tags=["auth"])

# Load environment variables
load_dotenv()

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS_PATH"))
    firebase_admin.initialize_app(cred)

def verify_firebase_token(authorization: str = Header(...)):
    """
    Verifies the Firebase ID token provided in the Authorization header.

    Args:
        request (Request): The current request.

    Returns:
        dict: The decoded Firebase ID token.

    Raises:
        HTTPException: If the Authorization header is missing or the token is invalid.
    """
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    id_token = authorization.split("Bearer ")[1]
    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token: " + str(e))


@router.get("/login")
def login(token_data=Depends(verify_firebase_token)):
    """
    Verifies the Firebase ID token provided in the Authorization header.
    Returns the user's UID if the token is valid.
    """
    uid = token_data['uid']
    return {"uid": uid}

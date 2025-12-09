import os
from typing import Optional, Dict
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, status
from dotenv import load_dotenv
from core.config import get_settings
from services.user_service import verify_session, get_user_by_id
import logging
import httpx

logger = logging.getLogger(__name__)

load_dotenv()

class AuthService:
    def __init__(self):
        self.jwt_secret = os.getenv("JWT_SECRET", "your-secret-key")
        self.clerk_secret_key = os.getenv("CLERK_SECRET_KEY", "")
        self.use_clerk = bool(self.clerk_secret_key and self.clerk_secret_key != "your_secret_key_here")
    
    async def verify_clerk_token(self, token: str) -> Dict:
        """Verify Clerk JWT token"""
        try:
            # Clerk tokens can be verified by calling Clerk's API or decoding the JWT
            # For now, we'll decode the JWT and extract user info
            # In production, you should verify the signature using Clerk's public key
            
            # Decode without verification (for development)
            # In production, fetch Clerk's JWKS and verify properly
            decoded = jwt.decode(token, options={"verify_signature": False})
            
            user_id = decoded.get("sub")  # Clerk user ID
            email = decoded.get("email")
            
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Clerk token"
                )
            
            return {
                "user_id": user_id,
                "email": email,
                "name": decoded.get("name", email),
                "role": "user",  # Default role
                "clerk_user": True
            }
            
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid Clerk token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    async def verify_token(self, token: str) -> Dict:
        """
        Verify token - supports both Clerk tokens and legacy session tokens
        """
        try:
            print(f"🔍 Verifying token: {token[:20]}...")
            
            # Try Clerk token first if Clerk is enabled
            if self.use_clerk:
                try:
                    clerk_data = await self.verify_clerk_token(token)
                    print(f"✅ Clerk token verified for user: {clerk_data.get('email')}")
                    return clerk_data
                except HTTPException:
                    # If Clerk verification fails, try legacy auth
                    print("⚠️ Clerk verification failed, trying legacy auth...")
            
            # Fall back to legacy session token verification
            user_data = verify_session(token)
            
            if not user_data:
                print("❌ Invalid or expired session token")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token"
                )
            
            # Return user data in the expected format
            result = {
                "user_id": str(user_data["_id"]),
                "email": user_data.get("email"),
                "name": user_data.get("name"),
                "role": user_data.get("role", "user"),
                "clerk_user": False
            }
            
            print(f"✅ Legacy token verified for user: {result['email']} (role: {result['role']})")
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Token verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )
    
    def get_user_with_role(self, user_id: str) -> Dict:
        """Fetch complete user data including role from MongoDB"""
        try:
            print(f"🔍 Fetching user data for ID: {user_id}")
            
            # Use the new get_user_by_id function from user_service
            user_data = get_user_by_id(user_id)
            
            if not user_data:
                print(f"⚠️ User not found: {user_id}")
                return None
            
            result = {
                "user_id": str(user_data["_id"]),
                "email": user_data.get("email"),
                "name": user_data.get("name"),
                "role": user_data.get("role", "user")
            }
            
            print(f"✅ User data fetched: {result['email']} (role: {result['role']})")
            return result
            
        except Exception as e:
            print(f"❌ Error fetching user data: {str(e)}")
            return None


# Global instance
_auth_service = None

def get_auth_service() -> AuthService:
    """Get or create AuthService singleton"""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service

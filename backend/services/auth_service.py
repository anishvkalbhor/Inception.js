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
        # Clerk publishable key for decoding JWT
        self.clerk_publishable_key = os.getenv("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY", "")
        
        # Check if Clerk is properly configured
        self.use_clerk = bool(
            self.clerk_secret_key 
            and self.clerk_secret_key.startswith("sk_")
        )
        
        if self.use_clerk:
            logger.info("✅ Clerk authentication enabled")
        else:
            logger.warning("⚠️ Clerk authentication disabled - using legacy auth only")
    
    def is_clerk_token(self, token: str) -> bool:
        """Check if token is a Clerk JWT (starts with eyJ and is longer than legacy tokens)"""
        try:
            # Clerk tokens are JWT format and much longer than our legacy session tokens
            if token.startswith("eyJ") and len(token) > 100:
                # Try to decode the header to confirm it's a JWT
                header = jwt.get_unverified_header(token)
                # Clerk uses RS256 algorithm
                return header.get("alg") == "RS256"
        except:
            pass
        return False
    
    async def verify_clerk_token(self, token: str) -> Dict:
        """Verify Clerk JWT token by decoding it"""
        try:
            # Decode the JWT without verification first to get session_id
            unverified_payload = jwt.decode(token, options={"verify_signature": False})
            session_id = unverified_payload.get("sid")
            user_id = unverified_payload.get("sub")
            
            if not session_id or not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Clerk token format"
                )
            
            # Verify the session is still active via Clerk API
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.clerk.com/v1/sessions/{session_id}",
                    headers={
                        "Authorization": f"Bearer {self.clerk_secret_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    logger.error(f"Clerk session verification failed: {response.status_code}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid or expired Clerk session"
                    )
                
                session_data = response.json()
                
                # Check if session is active
                if session_data.get("status") != "active":
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Clerk session is not active"
                    )
                
                # Fetch user data from Clerk
                user_response = await client.get(
                    f"https://api.clerk.com/v1/users/{user_id}",
                    headers={
                        "Authorization": f"Bearer {self.clerk_secret_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=10.0
                )
                
                if user_response.status_code != 200:
                    logger.error(f"Clerk user fetch failed: {user_response.status_code}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Failed to fetch user data"
                    )
                
                user_data = user_response.json()
                
                # Extract email and name
                email = None
                email_addresses = user_data.get("email_addresses", [])
                if email_addresses:
                    # Get primary email or first email
                    primary_email = next(
                        (e for e in email_addresses if e.get("is_primary")),
                        email_addresses[0]
                    )
                    email = primary_email.get("email_address")
                
                first_name = user_data.get("first_name", "")
                last_name = user_data.get("last_name", "")
                name = f"{first_name} {last_name}".strip() or email
                
                result = {
                    "user_id": user_id,
                    "email": email,
                    "name": name,
                    "role": "user",  # Default role for Clerk users
                    "clerk_user": True
                }
                
                logger.info(f"✅ Clerk token verified for user: {email}")
                return result
                
        except jwt.DecodeError:
            logger.error("Failed to decode Clerk JWT")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format"
            )
        except httpx.TimeoutException:
            logger.error("Clerk API timeout")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service unavailable"
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Clerk token verification error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token verification failed: {str(e)}"
            )
    
    async def verify_token(self, token: str) -> Dict:
        """
        Verify token - detects and routes to appropriate verification method
        """
        try:
            logger.info(f"🔍 Verifying token: {token[:20]}...")
            
            # Detect token type and route to appropriate verification
            if self.is_clerk_token(token):
                if not self.use_clerk:
                    logger.error("❌ Clerk token detected but Clerk is not configured")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Clerk authentication not configured"
                    )
                
                logger.info("🔑 Detected Clerk JWT token")
                return await self.verify_clerk_token(token)
            else:
                # Legacy session token
                logger.info("🔑 Detected legacy session token")
                user_data = verify_session(token)
                
                if not user_data:
                    logger.error("❌ Invalid or expired session token")
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
                
                logger.info(f"✅ Legacy token verified for user: {result['email']} (role: {result['role']})")
                return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Token verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )
    
    def get_user_with_role(self, user_id: str) -> Dict:
        """Fetch complete user data including role from MongoDB"""
        user = get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

# Global instance
_auth_service = None

def get_auth_service() -> AuthService:
    """Get or create AuthService singleton"""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
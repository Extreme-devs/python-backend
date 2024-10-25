from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from core.config import settings
from starlette.middleware.base import BaseHTTPMiddleware

SECRET_KEY = settings.JWT_SECRET_KEY


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(
                status_code=403,
                detail="Authentication credentials are missing or invalid",
            )
            return "Authentication credentials are missing or invalid"
        token = token[7:]  # Remove "Bearer " prefix
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(status_code=403, detail="Invalid token")
        except JWTError:
            raise HTTPException(status_code=403, detail="Invalid token")
        response = await call_next(request)
        return response

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from fastapi import Request, Depends, HTTPException
from app.config import JWT_ALGORITHM, JWT_SECRET_KEY
from jose import jwt
from app.schemas import UserRead

pass_man=CryptContext(schemes=["bcrypt"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")


async def get_current_user( request: Request,token: str = Depends(oauth2_scheme)):
    try:
        payload=jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    #except jwt.JWTError: for some reason JWTError isnt being identified proceedinf with exception
    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_id=payload.get('sub')
    if user_id is None:
        raise HTTPException(status_code=401, detail= "Unauthorized")
    async with request.state.db.acquire() as conn:
        async with conn.cursor() as curr:
            await curr.execute("SELECT id,username FROM users WHERE id =%s",(int(user_id),))
            user_fetched=await curr.fetchone()
        if not user_fetched: raise  HTTPException(status_code=401, detail="User not found")
        return UserRead(**user_fetched)

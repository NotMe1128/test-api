from fastapi import Request, HTTPException, APIRouter, Depends
import pymysql
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas import UserCreate, UserRead
from jose import jwt 
from datetime import datetime, timedelta,timezone
from app.config import JWT_ALGORITHM, JWT_SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
from app.dependencies import pass_man


user_router=APIRouter()

@user_router.post("/")
async def register(user_data:UserCreate, request: Request) -> UserRead:
    async with request.state.db.acquire() as conn:
        async with conn.cursor() as curr:
            hashed_pass=pass_man.hash(user_data.password)
            try:
                await curr.execute("INSERT INTO users(username, hashed_password) VALUES (%s,%s)", (user_data.username,hashed_pass))
            except pymysql.err.IntegrityError:
                raise HTTPException(status_code=400, detail="Username Already exists!")
            await curr.execute("SELECT id,username FROM users WHERE id =%s",(curr.lastrowid,))
            user_fetched=await curr.fetchone()
        return UserRead(**user_fetched)
    
@user_router.post("/token")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    async with request.state.db.acquire() as conn:
        async with conn.cursor() as curr:
            
            await curr.execute("SELECT id,username,hashed_password FROM users WHERE username =%s",(form_data.username,))
            user_fetched=await curr.fetchone()
            if curr.rowcount==0:
                raise HTTPException(status_code=404, detail="Username Not Found!")
            if not(pass_man.verify(form_data.password,user_fetched['hashed_password'])):
                raise HTTPException(status_code=401, detail="Incorrect Password")
            #token logic
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {"sub": str(user_fetched['id']), "exp": expire}
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return {"access_token": encoded_jwt, "token_type": "bearer"}



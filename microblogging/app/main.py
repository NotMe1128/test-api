from fastapi import FastAPI, Request
import datetime
from fastapi import Response
from contextlib import asynccontextmanager
from datetime import datetime,timezone
from app.routers import posts, users
from app.db import create_db
from app.config import RATE_LIMIT_DURATION, RATE_LIMIT_REQUESTS

app=FastAPI()

@asynccontextmanager
async def lifespan(app:FastAPI):
    pool = await create_db()
    app.state.db=pool 
    app.state.requests_count={}

    yield

    app.state.db.close()
    await app.state.db.wait_closed()

app = FastAPI(lifespan=lifespan)

app.include_router(posts.router,prefix='/posts',tags=["Posts"])
app.include_router(users.router,prefix='/users', tags=["Users"])


@app.middleware("http")
async def rate_limits(request: Request, call_next):
    ip_address=request.client.host
    now=datetime.now(timezone.utc)
    data = request.requests_counts.get(ip_address, [])
    new_data=[timestamp for timestamp in data if timestamp>(now-RATE_LIMIT_DURATION)]
    if len(new_data)>=RATE_LIMIT_REQUESTS:
        return Response("Too Many Requests", status_code=429)
    request.requests_counts[ip_address]=new_data
    request.requests_counts[ip_address].append(now)
    response = await call_next(request)
    return response


@app.get("/")
async def root():
    return {"message":"hi"}




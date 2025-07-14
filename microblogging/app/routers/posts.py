from fastapi import Request, APIRouter, Depends, HTTPException,Response
from typing import List
from app.schemas import PostCreate,PostRead,UserRead
from app.dependencies import get_current_user

post_router=APIRouter()


@post_router.post('/')
async def upload_post(post:PostCreate, request:Request,current_user: UserRead=Depends(get_current_user)):
    async with request.state.db.acquire() as conn:
        async with conn.cursor() as curr:
            await curr.execute("INSERT INTO posts(title, content, owner_id) VALUES(%s,%s,%s);",(post.title, post.content,current_user.id))
            await curr.execute("SELECT * FROM posts WHERE id= %s", (curr.lastrowid,))
            post_data=await curr.fetchone()
    if not(post_data):
        raise HTTPException(status_code=500, detail="Something went wrong")
    new_post=PostRead(**post_data)
    return new_post

@post_router.get("/")
async def retreive_post(request:Request) -> List[PostRead]:
    async with request.state.db.acquire() as conn:
        async with conn.cursor() as curr:
            await curr.execute("SELECT * FROM posts")
            data_fetched=await curr.fetchall()
    if data_fetched:
        return[PostRead(**post_data) for post_data in data_fetched]
    return []


@post_router.get("/{post_id}", responses={404: {"description": "Item not found"}})
async def retreive_post_id(post_id:int, request: Request) -> PostRead:
    async with request.state.db.acquire() as conn:
        async with conn.cursor() as curr:
            await curr.execute("SELECT * FROM posts WHERE id=%s",(post_id,))
            post_data=await curr.fetchone()
    if not(post_data):   
        raise HTTPException(status_code=404)
    ret_data= PostRead(**post_data)
    return ret_data


@post_router.put("/{post_id}", responses={404: {"description": "Item not found"}})
async def update_post(post_id:int, post_new:PostCreate, request: Request,current_user: UserRead=Depends(get_current_user)) -> PostRead:
    async with request.state.db.acquire() as conn:
        async with conn.cursor() as curr:
            await curr.execute("SELECT owner_id from posts where id=%s",(post_id,))
            o_id=await curr.fetchone()
            if not o_id:
                raise HTTPException(status_code=404, detail="Post not found")
            if int(o_id['owner_id'])!= current_user.id:
                raise HTTPException(status_code=403, detail="Get off bro ur not allowed to touch this, it aint urs")
            await curr.execute("UPDATE posts SET title=%s, content=%s where id=%s", (post_new.title, post_new.content,post_id))
            if curr.rowcount == 0:
                raise HTTPException(status_code=404)
            await curr.execute("SELECT * FROM posts WHERE id= %s", (post_id,))
            post_data=await curr.fetchone()
            return PostRead(**post_data)

@post_router.delete("/{post_id}", responses={404: {"description": "Item not found"}})
async def delete_post(post_id:int, request: Request, current_user:UserRead=Depends(get_current_user)) -> Response:
    async with request.state.db.acquire() as conn:
        async with conn.cursor() as curr:
            await curr.execute("SELECT owner_id from posts where id=%s",(post_id,))
            o_id=await curr.fetchone()
            if not o_id:
                raise HTTPException(status_code=404, detail="Post not found")
            if int(o_id['owner_id'])!= current_user.id:
                raise HTTPException(status_code=403, detail="Get off bro ur not allowed to touch this, it aint urs")
            await curr.execute("DELETE FROM posts WHERE id= %s",(post_id,))
            if curr.rowcount == 1:
                return Response(status_code=204)
        raise HTTPException(status_code=404)
    
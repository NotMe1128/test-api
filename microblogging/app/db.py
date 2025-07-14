import aiomysql
from app.config import USER,HOST,PASS,PORT,DB

async def create_db():
    pool=await aiomysql.create_pool(minsize=1,maxsize=5,user=USER,host=HOST,password=PASS,port=PORT,db=DB, autocommit=True,cursorclass=aiomysql.DictCursor)
    return pool
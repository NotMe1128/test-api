
import datetime
from pydantic import BaseModel




class PostCreate(BaseModel):
    title : str
    content: str

class PostRead(PostCreate):
    id: int
    upload_timestamp:datetime.datetime
    owner_id:int
    
class UserCreate(BaseModel):
    username: str
    password: str

class UserRead(BaseModel):
    id: int
    username: str

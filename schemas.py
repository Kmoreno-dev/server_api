from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    name: str

class UserLogin(BaseModel):
    username: str
    password: str

class PostCreate(BaseModel):
    title: str
    content: str
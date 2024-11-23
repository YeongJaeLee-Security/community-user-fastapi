from pydantic import BaseModel
from typing import Optional, List



class User(BaseModel):
    email: str
    password: str
    username: str
   


class UserSignIn(BaseModel):
    email: str
    password: str

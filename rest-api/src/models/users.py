from pydantic import BaseModel


class User(BaseModel):
    id: str
    user_login: str
    user_name: str
    user_description: str


class UserUpdate(BaseModel):
    user_login: str
    user_name: str
    user_description: str

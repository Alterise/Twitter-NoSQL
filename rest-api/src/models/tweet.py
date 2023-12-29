from pydantic import BaseModel


class Tweet(BaseModel):
    id: str
    user_login: str
    created_at: int
    tweet: str
    likes: int
    continent: str


class TweetUpdate(BaseModel):
    user_login: str
    created_at: int
    tweet: str
    likes: int
    continent: str

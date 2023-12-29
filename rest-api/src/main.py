from fastapi import FastAPI

from handler.event_handlers import startup, shutdown
from router.tweets_router import router as tweets_router
from router.users_router import router as users_router

app = FastAPI()

app.include_router(tweets_router, tags=["Tweets"], prefix="/api/tweets")
app.include_router(users_router, tags=["Users"], prefix="/api/users")
app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)

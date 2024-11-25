from contextlib import asynccontextmanager

from routers import auth, users, post
from fastapi import FastAPI
import uvicorn
from database.connection import connection
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    connection()
    yield

app = FastAPI(lifespan=lifespan)

# CORS(교차 출처 리소스 공유) 오류 해결
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PUT", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/auth")
app.include_router(auth.router)
app.include_router(post.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

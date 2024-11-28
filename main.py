from contextlib import asynccontextmanager
from routers import auth, user, post, report, notice
from fastapi import FastAPI
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
    allow_methods=["GET", "POST", "DELETE", "PUT", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

app.include_router(user.router, prefix="/auth", tags=["user"])
app.include_router(auth.router, tags=["auth"])
app.include_router(post.router, tags=["post"])
app.include_router(report.router, tags=["report"])
app.include_router(notice.router, tags=["notice"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )

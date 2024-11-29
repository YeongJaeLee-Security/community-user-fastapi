from contextlib import asynccontextmanager
from routers import auth, user, post, report, notice
from fastapi import FastAPI, HTTPException, status
from database.connection import connection
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from requests import Request

@asynccontextmanager
async def lifespan(app: FastAPI):
    connection()
    yield

app = FastAPI(lifespan=lifespan)

ALLOWED_REFERRERS = ["http://localhost:8000", "http://localhost:8010", "http://localhost:3000", "http://localhost:3010"]

# CORS(교차 출처 리소스 공유) 오류 해결
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PUT", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

@app.middleware("http")
async def verify_referer(request: Request, call_next):
    referer = request.headers.get("referer")
    if referer and not any(ref in referer for ref in ALLOWED_REFERRERS):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden from this origin")
    
    # 요청이 허용된 경우 다음 미들웨어 또는 엔드포인트로 전달
    response = await call_next(request)
    return response

app.include_router(user.router, prefix="/auth", tags=["user"])
app.include_router(auth.router, tags=["auth"])
app.include_router(post.router, tags=["post"])
app.include_router(report.router, tags=["report"])
app.include_router(notice.router, tags=["notice"])

app.mount("/uploaded_files", StaticFiles(directory="uploaded_files"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )

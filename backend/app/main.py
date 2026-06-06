from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.chapter_validation import router as chapter_validation_router
from backend.app.api.generate_script import router as generate_script_router


app = FastAPI(
    title="AI 小说转剧本工具 API",
    description="提供小说章节校验、AI 剧本生成和 YAML 校验相关接口。",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chapter_validation_router, prefix="/api", tags=["chapters"])
app.include_router(generate_script_router, prefix="/api", tags=["scripts"])


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}

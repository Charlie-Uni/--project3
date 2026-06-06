from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.app.services.chapter_parser import parse_chapters

router = APIRouter()


class ParseChaptersRequest(BaseModel):
    novel_text: str = Field(default="")


class ApiResponse(BaseModel):
    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None


@router.post("/parse-chapters", response_model=ApiResponse)
def parse_chapters_endpoint(request: ParseChaptersRequest) -> ApiResponse:
    result = parse_chapters(request.novel_text)

    return ApiResponse(
        success=True,
        data={
            "chapter_count": result.chapter_count,
            "word_count": result.word_count,
            "is_valid": result.is_valid,
            "message": result.message,
            "chapters": [
                {
                    "chapter_id": chapter.chapter_id,
                    "title": chapter.title,
                    "word_count": chapter.word_count,
                    "preview": chapter.content[:120],
                }
                for chapter in result.chapters
            ],
        },
        error=None,
    )

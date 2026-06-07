import logging
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.services.ai_script_generator import (
    ChapterRequirementError,
    ScriptGenerationError,
    ScriptGenerationInput,
    generate_script_yaml,
)

router = APIRouter()
logger = logging.getLogger(__name__)


class GenerateScriptRequest(BaseModel):
    novel_text: str = Field(..., min_length=1)
    source_title: str = "未命名小说"
    target_style: str = "screenplay_yaml"
    provider: str = "openai"


class ApiResponse(BaseModel):
    success: bool
    data: Optional[dict[str, Any]] = None
    error: Optional[str] = None


@router.post("/generate-script", response_model=ApiResponse)
async def generate_script(request: GenerateScriptRequest) -> ApiResponse:
    try:
        result = await generate_script_yaml(
            ScriptGenerationInput(
                novel_text=request.novel_text,
                source_title=request.source_title,
                target_style=request.target_style,
                provider=request.provider,
            )
        )
    except ChapterRequirementError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ScriptGenerationError as exc:
        logger.warning("AI 剧本生成失败: %s", exc)
        return ApiResponse(success=False, data=None, error=str(exc))
    except Exception:
        logger.exception("AI 剧本生成出现未知错误")
        return ApiResponse(success=False, data=None, error="服务器内部错误")

    has_validation_errors = len(result.validation_errors) > 0
    return ApiResponse(
        success=not has_validation_errors,
        data={
            "yaml_text": result.yaml_text,
            "parsed": result.parsed,
            "validation_errors": result.validation_errors,
            "chapter_count": result.chapter_count,
            "word_count": result.word_count,
            "used_mock": result.used_mock,
            "provider": result.provider,
            "model": result.model,
        },
        error="YAML 已生成，但未通过 Schema 校验" if has_validation_errors else None,
    )

import logging
import os
from pathlib import Path
from typing import Any

import yaml
from fastapi import APIRouter, HTTPException
from jsonschema import Draft202012Validator
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

router = APIRouter()
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = PROJECT_ROOT / "schemas" / "script.schema.yaml"
PROMPTS_DIR = PROJECT_ROOT / "prompts"


class GenerateScriptRequest(BaseModel):
    novel_text: str = Field(..., min_length=1)
    source_title: str = "未命名小说"
    target_style: str = "screenplay_yaml"
    chapter_count: int = Field(..., ge=3)
    word_count: int = 0


class ApiResponse(BaseModel):
    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None


def load_text_file(path: Path) -> str:
    if not path.exists():
        raise RuntimeError(f"文件不存在: {path}")
    return path.read_text(encoding="utf-8")


def load_schema() -> dict[str, Any]:
    try:
        return yaml.safe_load(load_text_file(SCHEMA_PATH))
    except Exception as exc:
        logger.exception("读取 Schema 失败")
        raise RuntimeError("Schema 文件读取失败") from exc


def parse_yaml(yaml_text: str) -> dict[str, Any]:
    try:
        parsed = yaml.safe_load(yaml_text)
    except yaml.YAMLError as exc:
        raise ValueError(f"YAML 解析失败: {exc}") from exc

    if not isinstance(parsed, dict):
        raise ValueError("YAML 顶层必须是 object")

    return parsed


def validate_script_yaml(parsed_yaml: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(parsed_yaml), key=lambda err: list(err.path))

    messages: list[str] = []
    for err in errors:
        field_path = ".".join(str(part) for part in err.path) or "root"
        messages.append(f"{field_path}: {err.message}")

    return messages


def strip_markdown_fence(text: str) -> str:
    cleaned = text.strip()
    if not cleaned.startswith("```"):
        return cleaned

    lines = cleaned.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def build_user_prompt(request: GenerateScriptRequest, schema: dict[str, Any]) -> str:
    template = load_text_file(PROMPTS_DIR / "user_prompt_template.txt")
    return template.format(
        novel_text=request.novel_text,
        source_title=request.source_title,
        chapter_count=request.chapter_count,
        word_count=request.word_count,
        target_style=request.target_style,
        generated_at="2026-06-06",
        schema_summary=yaml.safe_dump(schema, allow_unicode=True, sort_keys=False),
    )


def build_yaml_fix_prompt(invalid_yaml: str, parse_error: str) -> str:
    template = load_text_file(PROMPTS_DIR / "yaml_fix_prompt.txt")
    return template.format(
        invalid_yaml=invalid_yaml,
        parse_error=parse_error,
    )


def build_schema_retry_prompt(
    yaml_text: str,
    schema: dict[str, Any],
    validation_errors: list[str],
) -> str:
    template = load_text_file(PROMPTS_DIR / "schema_retry_prompt.txt")
    return template.format(
        yaml_text=yaml_text,
        schema_yaml=yaml.safe_dump(schema, allow_unicode=True, sort_keys=False),
        validation_errors="\n".join(validation_errors),
    )


def get_ai_client() -> AsyncOpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

    if not api_key:
        raise RuntimeError("缺少 OPENAI_API_KEY，请在后端环境变量中配置")

    return AsyncOpenAI(api_key=api_key, base_url=base_url)


async def call_ai(system_prompt: str, user_prompt: str) -> str:
    client = get_ai_client()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    try:
        response = await client.chat.completions.create(
            model=model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
    except Exception as exc:
        logger.exception("AI 调用失败")
        raise RuntimeError("AI 服务调用失败，请稍后重试或使用示例输出") from exc

    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("AI 返回内容为空")

    return strip_markdown_fence(content)


@router.post("/generate-script", response_model=ApiResponse)
async def generate_script(request: GenerateScriptRequest) -> ApiResponse:
    if request.chapter_count < 3:
        raise HTTPException(status_code=400, detail="小说输入至少需要 3 章")

    schema = load_schema()
    system_prompt = load_text_file(PROMPTS_DIR / "system_prompt.txt")
    user_prompt = build_user_prompt(request, schema)

    try:
        yaml_text = await call_ai(system_prompt, user_prompt)

        try:
            parsed = parse_yaml(yaml_text)
        except ValueError as exc:
            logger.warning("首次 YAML 解析失败，准备调用 YAML 修复 Prompt")
            fix_prompt = build_yaml_fix_prompt(yaml_text, str(exc))
            yaml_text = await call_ai(system_prompt, fix_prompt)
            parsed = parse_yaml(yaml_text)

        validation_errors = validate_script_yaml(parsed, schema)
        if validation_errors:
            logger.warning("首次 YAML Schema 校验失败，准备调用 Schema 重试 Prompt")
            retry_prompt = build_schema_retry_prompt(yaml_text, schema, validation_errors)

            # Schema 校验失败重试的调用位置。
            # 第二次调用只修复字段结构，不改变原剧情含义。
            yaml_text = await call_ai(system_prompt, retry_prompt)
            parsed = parse_yaml(yaml_text)
            validation_errors = validate_script_yaml(parsed, schema)

        if validation_errors:
            return ApiResponse(
                success=False,
                data={
                    "yaml_text": yaml_text,
                    "validation_errors": validation_errors,
                },
                error="YAML 已生成，但未通过 Schema 校验",
            )

        return ApiResponse(
            success=True,
            data={
                "yaml_text": yaml_text,
                "parsed": parsed,
                "validation_errors": [],
            },
            error=None,
        )

    except ValueError as exc:
        logger.warning("YAML 解析或格式错误: %s", exc)
        return ApiResponse(success=False, data=None, error=str(exc))

    except RuntimeError as exc:
        logger.warning("生成流程失败: %s", exc)
        return ApiResponse(success=False, data=None, error=str(exc))

    except Exception:
        logger.exception("未知错误")
        return ApiResponse(success=False, data=None, error="服务器内部错误")

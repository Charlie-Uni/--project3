import logging
import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from dotenv import load_dotenv
from openai import AsyncOpenAI

from backend.app.services.chapter_parser import ChapterParseResult, parse_chapters
from backend.app.services.yaml_validator import load_script_schema, validate_script_yaml

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")
PROMPTS_DIR = PROJECT_ROOT / "prompts"
SAMPLE_OUTPUT_PATH = PROJECT_ROOT / "examples" / "sample_output.yaml"
SUPPORTED_PROVIDER_ORDER = ["openai", "gemini", "deepseek"]


@dataclass(frozen=True)
class ProviderDefaults:
    display_name: str
    api_key_env: str
    base_url_env: str
    model_env: str
    default_base_url: str
    default_model: str


PROVIDER_DEFAULTS: Dict[str, ProviderDefaults] = {
    "openai": ProviderDefaults(
        display_name="OpenAI GPT",
        api_key_env="OPENAI_API_KEY",
        base_url_env="OPENAI_BASE_URL",
        model_env="OPENAI_MODEL",
        default_base_url="https://api.openai.com/v1",
        default_model="gpt-4o-mini",
    ),
    "gemini": ProviderDefaults(
        display_name="Gemini",
        api_key_env="GEMINI_API_KEY",
        base_url_env="GEMINI_BASE_URL",
        model_env="GEMINI_MODEL",
        default_base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        default_model="gemini-2.0-flash",
    ),
    "deepseek": ProviderDefaults(
        display_name="DeepSeek",
        api_key_env="DEEPSEEK_API_KEY",
        base_url_env="DEEPSEEK_BASE_URL",
        model_env="DEEPSEEK_MODEL",
        default_base_url="https://api.deepseek.com",
        default_model="deepseek-chat",
    ),
}


class ScriptGenerationError(Exception):
    pass


class ChapterRequirementError(ScriptGenerationError):
    pass


@dataclass
class ScriptGenerationInput:
    novel_text: str
    source_title: str
    target_style: str
    provider: str = "openai"


@dataclass
class ScriptGenerationResult:
    yaml_text: str
    parsed: Dict[str, Any]
    validation_errors: List[str]
    chapter_count: int
    word_count: int
    used_mock: bool
    provider: str
    model: str


@dataclass(frozen=True)
class AIProviderConfig:
    provider: str
    display_name: str
    api_key: str
    base_url: str
    model: str


def load_text_file(path: Path) -> str:
    if not path.exists():
        raise ScriptGenerationError(f"文件不存在: {path}")
    return path.read_text(encoding="utf-8")


def is_mock_ai_enabled() -> bool:
    value = os.getenv("USE_MOCK_AI", "true").strip().lower()
    return value in {"1", "true", "yes", "on"}


def normalize_provider(provider: Optional[str]) -> str:
    selected_provider = (provider or os.getenv("DEFAULT_AI_PROVIDER", "openai")).strip().lower()
    if selected_provider not in PROVIDER_DEFAULTS:
        supported = ", ".join(SUPPORTED_PROVIDER_ORDER)
        raise ScriptGenerationError(f"不支持的 AI 提供商: {selected_provider}，可选: {supported}")
    return selected_provider


def get_provider_model(provider: str) -> str:
    defaults = PROVIDER_DEFAULTS[provider]
    return os.getenv(defaults.model_env, defaults.default_model)


def get_ai_provider_config(provider: str) -> AIProviderConfig:
    defaults = PROVIDER_DEFAULTS[provider]
    api_key = os.getenv(defaults.api_key_env)

    if not api_key:
        raise ScriptGenerationError(f"缺少 {defaults.api_key_env}，请在后端环境变量中配置")

    return AIProviderConfig(
        provider=provider,
        display_name=defaults.display_name,
        api_key=api_key,
        base_url=os.getenv(defaults.base_url_env, defaults.default_base_url),
        model=get_provider_model(provider),
    )


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


def parse_yaml_object(yaml_text: str) -> Dict[str, Any]:
    parsed = yaml.safe_load(yaml_text)
    if not isinstance(parsed, dict):
        raise ScriptGenerationError("YAML 顶层必须是 object")
    return parsed


def build_user_prompt(
    generation_input: ScriptGenerationInput,
    chapter_result: ChapterParseResult,
    schema: Dict[str, Any],
) -> str:
    template = load_text_file(PROMPTS_DIR / "user_prompt_template.txt")
    return template.format(
        novel_text=generation_input.novel_text,
        source_title=generation_input.source_title,
        chapter_count=chapter_result.chapter_count,
        word_count=chapter_result.word_count,
        target_style=generation_input.target_style,
        generated_at=date.today().isoformat(),
        schema_summary=yaml.safe_dump(schema, allow_unicode=True, sort_keys=False),
    )


def build_yaml_fix_prompt(invalid_yaml: str, parse_error: str) -> str:
    template = load_text_file(PROMPTS_DIR / "yaml_fix_prompt.txt")
    return template.format(
        invalid_yaml=invalid_yaml,
        parse_error=parse_error,
    )


def build_schema_retry_prompt(yaml_text: str, schema: Dict[str, Any], validation_errors: List[str]) -> str:
    template = load_text_file(PROMPTS_DIR / "schema_retry_prompt.txt")
    return template.format(
        yaml_text=yaml_text,
        schema_yaml=yaml.safe_dump(schema, allow_unicode=True, sort_keys=False),
        validation_errors="\n".join(validation_errors),
    )


def get_ai_client(provider: str) -> tuple[AsyncOpenAI, AIProviderConfig]:
    config = get_ai_provider_config(provider)
    return AsyncOpenAI(api_key=config.api_key, base_url=config.base_url), config


async def call_ai(system_prompt: str, user_prompt: str, provider: str) -> str:
    client, config = get_ai_client(provider)

    try:
        response = await client.chat.completions.create(
            model=config.model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
    except Exception as exc:
        logger.exception("%s 调用失败", config.display_name)
        raise ScriptGenerationError("AI 服务调用失败，请稍后重试或启用 USE_MOCK_AI") from exc

    content = response.choices[0].message.content
    if not content:
        raise ScriptGenerationError("AI 返回内容为空")

    return strip_markdown_fence(content)


async def get_initial_yaml(system_prompt: str, user_prompt: str, provider: str) -> tuple[str, bool]:
    if is_mock_ai_enabled():
        return load_text_file(SAMPLE_OUTPUT_PATH), True
    return await call_ai(system_prompt, user_prompt, provider), False


async def normalize_generated_yaml(
    yaml_text: str,
    system_prompt: str,
    schema: Dict[str, Any],
    provider: str,
) -> tuple[str, Dict[str, Any], List[str]]:
    parse_result = validate_script_yaml(yaml_text)
    if not parse_result.is_parseable and not is_mock_ai_enabled():
        logger.warning("首次 YAML 解析失败，准备调用 YAML 修复 Prompt")
        fix_prompt = build_yaml_fix_prompt(yaml_text, "\n".join(parse_result.errors))
        yaml_text = await call_ai(system_prompt, fix_prompt, provider)
        parse_result = validate_script_yaml(yaml_text)

    if not parse_result.is_parseable:
        raise ScriptGenerationError("YAML 解析失败: " + "; ".join(parse_result.errors))

    if not parse_result.is_valid and not is_mock_ai_enabled():
        logger.warning("首次 YAML Schema 校验失败，准备调用 Schema 重试 Prompt")
        retry_prompt = build_schema_retry_prompt(yaml_text, schema, parse_result.errors)
        yaml_text = await call_ai(system_prompt, retry_prompt, provider)
        parse_result = validate_script_yaml(yaml_text)

    parsed = parse_yaml_object(yaml_text)
    return yaml_text, parsed, parse_result.errors


async def generate_script_yaml(generation_input: ScriptGenerationInput) -> ScriptGenerationResult:
    provider = normalize_provider(generation_input.provider)
    chapter_result = parse_chapters(generation_input.novel_text)
    if not chapter_result.is_valid:
        raise ChapterRequirementError(chapter_result.message)

    schema = load_script_schema()
    system_prompt = load_text_file(PROMPTS_DIR / "system_prompt.txt")
    user_prompt = build_user_prompt(generation_input, chapter_result, schema)

    yaml_text, used_mock = await get_initial_yaml(system_prompt, user_prompt, provider)
    yaml_text, parsed, validation_errors = await normalize_generated_yaml(yaml_text, system_prompt, schema, provider)

    return ScriptGenerationResult(
        yaml_text=yaml_text,
        parsed=parsed,
        validation_errors=validation_errors,
        chapter_count=chapter_result.chapter_count,
        word_count=chapter_result.word_count,
        used_mock=used_mock,
        provider=provider,
        model=get_provider_model(provider),
    )

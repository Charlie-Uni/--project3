from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_SCHEMA_PATH = PROJECT_ROOT / "schemas" / "script.schema.yaml"


@dataclass
class YamlValidationResult:
    is_parseable: bool
    is_valid: bool
    message: str
    errors: list[str]
    top_level_fields: list[str]


def load_script_schema() -> dict[str, Any]:
    schema_text = SCRIPT_SCHEMA_PATH.read_text(encoding="utf-8")
    schema = yaml.safe_load(schema_text)
    if not isinstance(schema, dict):
        raise RuntimeError("Schema 顶层必须是 object")
    return schema


def validate_script_yaml(yaml_text: str) -> YamlValidationResult:
    if not yaml_text.strip():
        return YamlValidationResult(
            is_parseable=False,
            is_valid=False,
            message="请输入 YAML 文本",
            errors=["YAML 文本不能为空"],
            top_level_fields=[],
        )

    try:
        parsed_yaml = yaml.safe_load(yaml_text)
    except yaml.YAMLError as exc:
        return YamlValidationResult(
            is_parseable=False,
            is_valid=False,
            message="YAML 解析失败",
            errors=[str(exc)],
            top_level_fields=[],
        )

    if not isinstance(parsed_yaml, dict):
        return YamlValidationResult(
            is_parseable=True,
            is_valid=False,
            message="YAML 顶层必须是 object",
            errors=["root: YAML 顶层必须是 object"],
            top_level_fields=[],
        )

    schema = load_script_schema()
    validator = Draft202012Validator(schema)
    validation_errors = sorted(validator.iter_errors(parsed_yaml), key=lambda err: list(err.path))
    errors = [format_validation_error(error) for error in validation_errors]

    if errors:
        return YamlValidationResult(
            is_parseable=True,
            is_valid=False,
            message="YAML 未通过 Schema 校验",
            errors=errors,
            top_level_fields=list(parsed_yaml.keys()),
        )

    return YamlValidationResult(
        is_parseable=True,
        is_valid=True,
        message="YAML 已通过 Schema 校验",
        errors=[],
        top_level_fields=list(parsed_yaml.keys()),
    )


def format_validation_error(error: Any) -> str:
    field_path = ".".join(str(part) for part in error.path) or "root"
    return f"{field_path}: {error.message}"

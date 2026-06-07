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
    summary: dict[str, int]
    characters_preview: list[dict[str, Any]]
    scenes_preview: list[dict[str, Any]]


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
            summary=empty_summary(),
            characters_preview=[],
            scenes_preview=[],
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
            summary=empty_summary(),
            characters_preview=[],
            scenes_preview=[],
        )

    if not isinstance(parsed_yaml, dict):
        return YamlValidationResult(
            is_parseable=True,
            is_valid=False,
            message="YAML 顶层必须是 object",
            errors=["root: YAML 顶层必须是 object"],
            top_level_fields=[],
            summary=empty_summary(),
            characters_preview=[],
            scenes_preview=[],
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
            summary=extract_script_summary(parsed_yaml),
            characters_preview=extract_characters_preview(parsed_yaml),
            scenes_preview=extract_scenes_preview(parsed_yaml),
        )

    return YamlValidationResult(
        is_parseable=True,
        is_valid=True,
        message="YAML 已通过 Schema 校验",
        errors=[],
        top_level_fields=list(parsed_yaml.keys()),
        summary=extract_script_summary(parsed_yaml),
        characters_preview=extract_characters_preview(parsed_yaml),
        scenes_preview=extract_scenes_preview(parsed_yaml),
    )


def format_validation_error(error: Any) -> str:
    field_path = ".".join(str(part) for part in error.path) or "root"
    return f"{field_path}: {error.message}"


def empty_summary() -> dict[str, int]:
    return {
        "character_count": 0,
        "chapter_count": 0,
        "scene_count": 0,
        "dialogue_count": 0,
    }


def extract_script_summary(parsed_yaml: dict[str, Any]) -> dict[str, int]:
    characters = get_list(parsed_yaml.get("characters"))
    chapters = get_list(parsed_yaml.get("chapters"))
    scenes = get_list(get_dict(parsed_yaml.get("script")).get("scenes"))
    dialogue_count = 0

    for scene in scenes:
        if isinstance(scene, dict):
            dialogue_count += len(get_list(scene.get("dialogues")))

    return {
        "character_count": len(characters),
        "chapter_count": len(chapters),
        "scene_count": len(scenes),
        "dialogue_count": dialogue_count,
    }


def extract_characters_preview(parsed_yaml: dict[str, Any]) -> list[dict[str, Any]]:
    characters = get_list(parsed_yaml.get("characters"))
    preview: list[dict[str, Any]] = []

    for character in characters[:8]:
        if not isinstance(character, dict):
            continue
        preview.append(
            {
                "name": str(character.get("name", "未知")),
                "role": str(character.get("role", "unknown")),
                "description": str(character.get("description", "")),
                "traits": get_list(character.get("traits"))[:4],
            }
        )

    return preview


def extract_scenes_preview(parsed_yaml: dict[str, Any]) -> list[dict[str, Any]]:
    scenes = get_list(get_dict(parsed_yaml.get("script")).get("scenes"))
    preview: list[dict[str, Any]] = []

    for scene in scenes[:12]:
        if not isinstance(scene, dict):
            continue
        preview.append(
            {
                "scene_id": str(scene.get("scene_id", "未知")),
                "source_chapter": str(scene.get("source_chapter", "未知")),
                "location": str(scene.get("location", "未知")),
                "time": str(scene.get("time", "未知")),
                "summary": str(scene.get("summary", "")),
                "characters_in_scene": get_list(scene.get("characters_in_scene")),
                "dialogue_count": len(get_list(scene.get("dialogues"))),
                "conflicts": to_string_list(scene.get("conflicts"))[:3],
                "plot_points": to_string_list(scene.get("plot_points"))[:4],
                "actions": extract_actions_preview(scene),
                "dialogues": extract_dialogues_preview(scene),
                "narration": extract_narration_preview(scene),
                "emotions": extract_emotions_preview(scene),
                "transition": extract_transition_preview(scene),
            }
        )

    return preview


def extract_actions_preview(scene: dict[str, Any]) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []

    for action in get_list(scene.get("actions"))[:4]:
        if not isinstance(action, dict):
            continue
        actions.append(
            {
                "actor": str(action.get("actor", "未知")),
                "description": str(action.get("description", "")),
            }
        )

    return actions


def extract_dialogues_preview(scene: dict[str, Any]) -> list[dict[str, str]]:
    dialogues: list[dict[str, str]] = []

    for dialogue in get_list(scene.get("dialogues"))[:4]:
        if not isinstance(dialogue, dict):
            continue
        dialogues.append(
            {
                "speaker": str(dialogue.get("speaker", "未知")),
                "line": str(dialogue.get("line", "")),
                "emotion": str(dialogue.get("emotion", "")),
            }
        )

    return dialogues


def extract_narration_preview(scene: dict[str, Any]) -> list[dict[str, str]]:
    narration_items: list[dict[str, str]] = []

    for narration in get_list(scene.get("narration"))[:3]:
        if not isinstance(narration, dict):
            continue
        narration_items.append(
            {
                "type": str(narration.get("type", "")),
                "text": str(narration.get("text", "")),
            }
        )

    return narration_items


def extract_emotions_preview(scene: dict[str, Any]) -> list[dict[str, str]]:
    emotions: list[dict[str, str]] = []

    for emotion in get_list(scene.get("emotions"))[:4]:
        if not isinstance(emotion, dict):
            continue
        emotions.append(
            {
                "character": str(emotion.get("character", "未知")),
                "emotion": str(emotion.get("emotion", "")),
                "evidence": str(emotion.get("evidence", "")),
            }
        )

    return emotions


def extract_transition_preview(scene: dict[str, Any]) -> dict[str, str]:
    transition = get_dict(scene.get("transitions"))
    return {
        "type": str(transition.get("type", "")),
        "next_scene_id": str(transition.get("next_scene_id", "")),
        "description": str(transition.get("description", "")),
    }


def get_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def get_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def to_string_list(value: Any) -> list[str]:
    return [str(item) for item in get_list(value)]

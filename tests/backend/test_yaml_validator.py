from pathlib import Path

from backend.app.services.yaml_validator import validate_script_yaml


def test_validate_sample_output_yaml() -> None:
    yaml_text = Path("examples/sample_output.yaml").read_text(encoding="utf-8")

    result = validate_script_yaml(yaml_text)

    assert result.is_parseable is True
    assert result.is_valid is True
    assert result.errors == []
    assert result.summary == {
        "character_count": 3,
        "chapter_count": 3,
        "scene_count": 2,
        "dialogue_count": 2,
    }
    assert result.characters_preview[0]["name"] == "林夏"
    assert result.scenes_preview[0]["scene_id"] == "sc_001"
    assert result.scenes_preview[0]["actions"][0]["actor"] == "林夏"
    assert result.scenes_preview[0]["narration"][0]["type"] == "voice_over"
    assert result.scenes_preview[0]["emotions"][0]["character"] == "林夏"
    assert result.scenes_preview[1]["dialogues"][0]["speaker"] == "林夏"
    assert result.scenes_preview[1]["transition"]["type"] == "fade_out"


def test_validate_yaml_reports_schema_errors() -> None:
    yaml_text = "metadata: test"

    result = validate_script_yaml(yaml_text)

    assert result.is_parseable is True
    assert result.is_valid is False
    assert result.errors
    assert any("source_info" in error for error in result.errors)


def test_validate_yaml_reports_parse_errors() -> None:
    yaml_text = "metadata: ["

    result = validate_script_yaml(yaml_text)

    assert result.is_parseable is False
    assert result.is_valid is False
    assert result.errors

from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_generate_script_uses_mock_yaml(monkeypatch) -> None:
    monkeypatch.setenv("USE_MOCK_AI", "true")
    novel_text = Path("examples/sample_novel.txt").read_text(encoding="utf-8")

    response = client.post(
        "/api/generate-script",
        json={
            "novel_text": novel_text,
            "source_title": "雨夜来信",
            "target_style": "screenplay_yaml",
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["success"] is True
    assert data["data"]["used_mock"] is True
    assert data["data"]["validation_errors"] == []
    assert data["data"]["parsed"]["metadata"]["title"] == "雨夜来信"
    assert data["data"]["provider"] == "openai"
    assert data["data"]["model"] == "gpt-4o-mini"


def test_generate_script_accepts_gemini_provider_in_mock(monkeypatch) -> None:
    monkeypatch.setenv("USE_MOCK_AI", "true")
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    novel_text = Path("examples/sample_novel.txt").read_text(encoding="utf-8")

    response = client.post(
        "/api/generate-script",
        json={
            "novel_text": novel_text,
            "source_title": "雨夜来信",
            "target_style": "screenplay_yaml",
            "provider": "gemini",
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["success"] is True
    assert data["data"]["used_mock"] is True
    assert data["data"]["provider"] == "gemini"
    assert data["data"]["model"] == "gemini-2.0-flash"


def test_generate_script_rejects_unknown_provider(monkeypatch) -> None:
    monkeypatch.setenv("USE_MOCK_AI", "true")
    novel_text = Path("examples/sample_novel.txt").read_text(encoding="utf-8")

    response = client.post(
        "/api/generate-script",
        json={
            "novel_text": novel_text,
            "source_title": "雨夜来信",
            "provider": "claude",
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["success"] is False
    assert "不支持的 AI 提供商" in data["error"]


def test_generate_script_rejects_less_than_three_chapters(monkeypatch) -> None:
    monkeypatch.setenv("USE_MOCK_AI", "true")

    response = client.post(
        "/api/generate-script",
        json={
            "novel_text": "第1章 开始\n只有一章。",
            "source_title": "短文本",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "小说文本至少需要包含 3 个章节"


def test_generate_script_reports_missing_api_key(monkeypatch) -> None:
    monkeypatch.setenv("USE_MOCK_AI", "false")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    novel_text = Path("examples/sample_novel.txt").read_text(encoding="utf-8")

    response = client.post(
        "/api/generate-script",
        json={
            "novel_text": novel_text,
            "source_title": "雨夜来信",
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["success"] is False
    assert "OPENAI_API_KEY" in data["error"]

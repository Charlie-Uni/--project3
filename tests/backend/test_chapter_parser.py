from backend.app.services.chapter_parser import parse_chapters


def test_parse_chapters_with_chinese_headings() -> None:
    text = """
第1章 雨夜
林夏在办公室加班。

第2章 信封
顾沉带来一封信。

第3章 旧楼
两人前往旧楼。
"""

    result = parse_chapters(text)

    assert result.is_valid is True
    assert result.chapter_count == 3
    assert [chapter.chapter_id for chapter in result.chapters] == ["ch_001", "ch_002", "ch_003"]
    assert result.chapters[0].title == "第1章 雨夜"


def test_parse_chapters_rejects_less_than_three_chapters() -> None:
    text = """
第1章 开始
只有第一章。

第2章 继续
只有第二章。
"""

    result = parse_chapters(text)

    assert result.is_valid is False
    assert result.chapter_count == 2
    assert result.message == "小说文本至少需要包含 3 个章节"


def test_parse_chapters_with_manual_separators() -> None:
    text = """
雨夜
第一段内容。
---
信封
第二段内容。
---
旧楼
第三段内容。
"""

    result = parse_chapters(text)

    assert result.is_valid is True
    assert result.chapter_count == 3
    assert result.chapters[0].title == "雨夜"

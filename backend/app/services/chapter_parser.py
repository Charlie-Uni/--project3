import re
from dataclasses import dataclass


CHAPTER_HEADING_PATTERN = re.compile(
    r"^\s*((?:第[一二三四五六七八九十百千万两0-9\d]+章|Chapter\s+\d+|CHAPTER\s+\d+)[^\n\r]*)\s*$",
    re.MULTILINE,
)

SEPARATOR_PATTERN = re.compile(r"^\s*(?:---+|\*\*\*+)\s*$", re.MULTILINE)


@dataclass
class Chapter:
    chapter_id: str
    title: str
    content: str
    word_count: int


@dataclass
class ChapterParseResult:
    chapter_count: int
    word_count: int
    is_valid: bool
    message: str
    chapters: list[Chapter]


def count_chinese_text_units(text: str) -> int:
    compact_text = re.sub(r"\s+", "", text)
    return len(compact_text)


def parse_chapters(novel_text: str) -> ChapterParseResult:
    normalized_text = novel_text.strip()
    if not normalized_text:
        return ChapterParseResult(
            chapter_count=0,
            word_count=0,
            is_valid=False,
            message="请输入小说文本",
            chapters=[],
        )

    chapters = parse_by_headings(normalized_text)
    if not chapters:
        chapters = parse_by_separators(normalized_text)

    chapter_count = len(chapters)
    word_count = count_chinese_text_units(normalized_text)
    is_valid = chapter_count >= 3
    message = "章节数量满足要求" if is_valid else "小说文本至少需要包含 3 个章节"

    return ChapterParseResult(
        chapter_count=chapter_count,
        word_count=word_count,
        is_valid=is_valid,
        message=message,
        chapters=chapters,
    )


def parse_by_headings(text: str) -> list[Chapter]:
    matches = list(CHAPTER_HEADING_PATTERN.finditer(text))
    if not matches:
        return []

    chapters: list[Chapter] = []
    for index, match in enumerate(matches):
        title = match.group(1).strip()
        content_start = match.end()
        content_end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        content = text[content_start:content_end].strip()
        chapters.append(
            Chapter(
                chapter_id=f"ch_{index + 1:03d}",
                title=title,
                content=content,
                word_count=count_chinese_text_units(content),
            )
        )

    return chapters


def parse_by_separators(text: str) -> list[Chapter]:
    parts = [part.strip() for part in SEPARATOR_PATTERN.split(text) if part.strip()]
    chapters: list[Chapter] = []

    for index, part in enumerate(parts):
        first_line = part.splitlines()[0].strip()
        title = first_line if len(first_line) <= 30 else f"第 {index + 1} 章"
        chapters.append(
            Chapter(
                chapter_id=f"ch_{index + 1:03d}",
                title=title,
                content=part,
                word_count=count_chinese_text_units(part),
            )
        )

    return chapters

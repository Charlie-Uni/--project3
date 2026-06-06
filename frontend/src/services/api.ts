const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export type ChapterPreview = {
  chapter_id: string;
  title: string;
  word_count: number;
  preview: string;
};

export type ParseChaptersData = {
  chapter_count: number;
  word_count: number;
  is_valid: boolean;
  message: string;
  chapters: ChapterPreview[];
};

export type ApiResponse<T> = {
  success: boolean;
  data: T | null;
  error: string | null;
};

export async function parseChapters(novelText: string): Promise<ApiResponse<ParseChaptersData>> {
  const response = await fetch(`${API_BASE_URL}/api/parse-chapters`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      novel_text: novelText
    })
  });

  if (!response.ok) {
    throw new Error(`章节校验接口异常: ${response.status}`);
  }

  return response.json();
}

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

export type ValidateYamlData = {
  is_parseable: boolean;
  is_valid: boolean;
  message: string;
  errors: string[];
  top_level_fields: string[];
};

export type GenerateScriptData = {
  yaml_text: string;
  parsed: Record<string, unknown>;
  validation_errors: string[];
  chapter_count: number;
  word_count: number;
  used_mock: boolean;
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

export async function validateYaml(yamlText: string): Promise<ApiResponse<ValidateYamlData>> {
  const response = await fetch(`${API_BASE_URL}/api/validate-yaml`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      yaml_text: yamlText
    })
  });

  if (!response.ok) {
    throw new Error(`YAML 校验接口异常: ${response.status}`);
  }

  return response.json();
}

export async function generateScript(
  novelText: string,
  sourceTitle: string,
  targetStyle = "screenplay_yaml"
): Promise<ApiResponse<GenerateScriptData>> {
  const response = await fetch(`${API_BASE_URL}/api/generate-script`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      novel_text: novelText,
      source_title: sourceTitle || "未命名小说",
      target_style: targetStyle
    })
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);
    throw new Error(errorBody?.detail || `AI 剧本生成接口异常: ${response.status}`);
  }

  return response.json();
}

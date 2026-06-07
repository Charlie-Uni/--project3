import {
  BookOpen,
  CheckCircle2,
  Download,
  FileText,
  Loader2,
  RotateCcw,
  ScanText,
  WandSparkles
} from "lucide-react";
import { useMemo, useState } from "react";
import {
  generateScript,
  parseChapters,
  validateYaml,
  type AiProvider,
  type ChapterPreview,
  type ValidateYamlData
} from "./services/api";
import { ParticleBackground } from "./components/ParticleBackground";
import { StickmanSceneDemo } from "./components/StickmanSceneDemo";

type ValidationState = {
  chapterCount: number;
  wordCount: number;
  isValid: boolean;
  message: string;
  chapters: ChapterPreview[];
};

const EMPTY_RESULT: ValidationState = {
  chapterCount: 0,
  wordCount: 0,
  isValid: false,
  message: "等待输入小说文本",
  chapters: []
};

const EMPTY_YAML_RESULT: ValidateYamlData = {
  is_parseable: false,
  is_valid: false,
  message: "等待输入 YAML 文本",
  errors: [],
  top_level_fields: [],
  summary: {
    character_count: 0,
    chapter_count: 0,
    scene_count: 0,
    dialogue_count: 0
  },
  characters_preview: [],
  scenes_preview: []
};

type WorkMode = "novel" | "yaml";

const AI_PROVIDER_OPTIONS: Array<{ value: AiProvider; label: string; description: string }> = [
  {
    value: "openai",
    label: "OpenAI GPT",
    description: "通用剧本生成"
  },
  {
    value: "gemini",
    label: "Gemini",
    description: "长文本理解"
  },
  {
    value: "deepseek",
    label: "DeepSeek",
    description: "低成本生成"
  }
];

function getProviderLabel(provider: AiProvider) {
  return AI_PROVIDER_OPTIONS.find((option) => option.value === provider)?.label || provider;
}

function App() {
  const [mode, setMode] = useState<WorkMode>("novel");
  const [sourceTitle, setSourceTitle] = useState("雨夜来信");
  const [selectedProvider, setSelectedProvider] = useState<AiProvider>("openai");
  const [novelText, setNovelText] = useState("");
  const [result, setResult] = useState<ValidationState>(EMPTY_RESULT);
  const [error, setError] = useState("");
  const [isChecking, setIsChecking] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationMessage, setGenerationMessage] = useState("");
  const [yamlText, setYamlText] = useState("");
  const [yamlResult, setYamlResult] = useState<ValidateYamlData>(EMPTY_YAML_RESULT);
  const [yamlError, setYamlError] = useState("");
  const [isValidatingYaml, setIsValidatingYaml] = useState(false);

  const canCheck = novelText.trim().length > 0 && !isChecking;
  const canGenerate = novelText.trim().length > 0 && result.isValid && !isGenerating;
  const canValidateYaml = yamlText.trim().length > 0 && !isValidatingYaml;
  const isCurrentModeValid = mode === "yaml" ? yamlResult.is_valid : result.isValid;

  const statusLabel = useMemo(() => {
    if (mode === "yaml") {
      if (isValidatingYaml) return "校验中";
      if (yamlError) return "校验失败";
      return yamlResult.is_valid ? "Schema 通过" : "等待 YAML";
    }

    if (isChecking) return "校验中";
    if (error) return "校验失败";
    return result.isValid ? "可生成剧本" : "需要补充章节";
  }, [error, isChecking, isValidatingYaml, mode, result.isValid, yamlError, yamlResult.is_valid]);

  async function handleCheck() {
    if (!novelText.trim()) {
      setError("请输入小说文本");
      setResult(EMPTY_RESULT);
      return;
    }

    setIsChecking(true);
    setError("");

    try {
      const response = await parseChapters(novelText);
      if (!response.success || !response.data) {
        throw new Error(response.error || "章节校验失败");
      }

      setResult({
        chapterCount: response.data.chapter_count,
        wordCount: response.data.word_count,
        isValid: response.data.is_valid,
        message: response.data.message,
        chapters: response.data.chapters
      });
    } catch (requestError) {
      setResult(EMPTY_RESULT);
      setError(requestError instanceof Error ? requestError.message : "章节校验失败");
    } finally {
      setIsChecking(false);
    }
  }

  async function handleLoadSample() {
    setIsChecking(true);
    setError("");

    try {
      const response = await fetch("/sample_novel.txt");
      if (!response.ok) {
        throw new Error("示例文本加载失败");
      }
      const sampleText = await response.text();
      setNovelText(sampleText);
      setSourceTitle("雨夜来信");
      setResult(EMPTY_RESULT);
      setGenerationMessage("");
    } catch (sampleError) {
      setError(sampleError instanceof Error ? sampleError.message : "示例文本加载失败");
    } finally {
      setIsChecking(false);
    }
  }

  function handleReset() {
    setNovelText("");
    setResult(EMPTY_RESULT);
    setError("");
    setGenerationMessage("");
  }

  async function handleGenerateScript() {
    if (!result.isValid) {
      setError("请先完成章节校验，并确保小说不少于 3 章");
      return;
    }

    setIsGenerating(true);
    setError("");
    setGenerationMessage("");

    try {
      const response = await generateScript(novelText, sourceTitle, "screenplay_yaml", selectedProvider);
      if (!response.success || !response.data) {
        throw new Error(response.error || "AI 剧本生成失败");
      }

      setYamlText(response.data.yaml_text);
      const validationResponse = await validateYaml(response.data.yaml_text);
      if (validationResponse.success && validationResponse.data) {
        setYamlResult(validationResponse.data);
      } else {
        setYamlResult({
          ...EMPTY_YAML_RESULT,
          is_parseable: true,
          is_valid: response.data.validation_errors.length === 0,
          message:
            response.data.validation_errors.length === 0
              ? "AI 生成结果已通过 Schema 校验"
              : "AI 生成结果未通过 Schema 校验",
          errors: response.data.validation_errors,
          top_level_fields: Object.keys(response.data.parsed)
        });
      }
      setGenerationMessage(
        response.data.used_mock
          ? `已使用示例 YAML 生成结果。当前选择 ${getProviderLabel(response.data.provider)}，关闭 mock 后将调用 ${response.data.model}。`
          : `${getProviderLabel(response.data.provider)} 已生成剧本 YAML，使用模型 ${response.data.model}。`
      );
      setMode("yaml");
    } catch (generateError) {
      setError(generateError instanceof Error ? generateError.message : "AI 剧本生成失败");
    } finally {
      setIsGenerating(false);
    }
  }

  async function handleValidateYaml() {
    if (!yamlText.trim()) {
      setYamlError("请输入 YAML 文本");
      setYamlResult(EMPTY_YAML_RESULT);
      return;
    }

    setIsValidatingYaml(true);
    setYamlError("");

    try {
      const response = await validateYaml(yamlText);
      if (!response.success || !response.data) {
        throw new Error(response.error || "YAML 校验失败");
      }
      setYamlResult(response.data);
    } catch (requestError) {
      setYamlResult(EMPTY_YAML_RESULT);
      setYamlError(requestError instanceof Error ? requestError.message : "YAML 校验失败");
    } finally {
      setIsValidatingYaml(false);
    }
  }

  function handleResetYaml() {
    setYamlText("");
    setYamlResult(EMPTY_YAML_RESULT);
    setYamlError("");
  }

  function handleExportYaml() {
    if (!yamlText.trim()) {
      setYamlError("请先生成或输入 YAML 文本");
      return;
    }

    const blob = new Blob([yamlText], { type: "text/yaml;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    const safeTitle = (sourceTitle || "script").trim().replace(/[\\/:*?"<>|]/g, "_");
    link.href = url;
    link.download = `${safeTitle || "script"}.yaml`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  async function handleLoadSampleYaml() {
    setIsValidatingYaml(true);
    setYamlError("");

    try {
      const response = await fetch("/sample_output.yaml");
      if (!response.ok) {
        throw new Error("示例 YAML 加载失败");
      }
      const sampleYaml = await response.text();
      setYamlText(sampleYaml);
      setYamlResult(EMPTY_YAML_RESULT);
    } catch (sampleError) {
      setYamlError(sampleError instanceof Error ? sampleError.message : "示例 YAML 加载失败");
    } finally {
      setIsValidatingYaml(false);
    }
  }

  return (
    <main className="app-shell">
      <ParticleBackground />
      <section className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">AI 小说转剧本工具</p>
            <h1>{mode === "novel" ? "小说输入与章节校验" : "YAML Schema 校验"}</h1>
          </div>
          <div className={`status-pill ${isCurrentModeValid ? "valid" : "invalid"}`}>
            {statusLabel}
          </div>
        </header>

        <nav className="mode-tabs" aria-label="功能切换">
          <button className={mode === "novel" ? "active" : ""} onClick={() => setMode("novel")}>
            <FileText size={18} />
            小说章节校验
          </button>
          <button className={mode === "yaml" ? "active" : ""} onClick={() => setMode("yaml")}>
            <CheckCircle2 size={18} />
            YAML Schema 校验
          </button>
        </nav>

        {mode === "novel" ? (
          <div className="layout-grid">
          <section className="input-panel">
            <div className="panel-heading">
              <FileText size={20} />
              <h2>小说文本</h2>
            </div>
            <label className="field-label" htmlFor="source-title">
              小说标题
            </label>
            <input
              id="source-title"
              value={sourceTitle}
              onChange={(event) => setSourceTitle(event.target.value)}
              placeholder="请输入小说标题"
            />
            <div className="provider-selector" aria-label="AI 模型选择">
              <span>AI 模型</span>
              <div className="provider-options">
                {AI_PROVIDER_OPTIONS.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    className={selectedProvider === option.value ? "active" : ""}
                    onClick={() => setSelectedProvider(option.value)}
                  >
                    <strong>{option.label}</strong>
                    <small>{option.description}</small>
                  </button>
                ))}
              </div>
            </div>
            <textarea
              value={novelText}
              onChange={(event) => setNovelText(event.target.value)}
              placeholder="请粘贴至少 3 章小说文本，例如: 第1章 ... 第2章 ... 第3章 ..."
              spellCheck={false}
            />
            <div className="actions">
              <button className="secondary-button" onClick={handleLoadSample} disabled={isChecking}>
                <BookOpen size={18} />
                加载示例
              </button>
              <button className="primary-button" disabled={!canCheck} onClick={handleCheck}>
                {isChecking ? <Loader2 className="spin" size={18} /> : <ScanText size={18} />}
                校验章节
              </button>
              <button className="primary-button" disabled={!canGenerate} onClick={handleGenerateScript}>
                {isGenerating ? <Loader2 className="spin" size={18} /> : <WandSparkles size={18} />}
                生成剧本 YAML
              </button>
              <button className="secondary-button" onClick={handleReset}>
                <RotateCcw size={18} />
                清空
              </button>
            </div>
          </section>

          <section className="result-panel">
            <div className="panel-heading">
              <ScanText size={20} />
              <h2>校验结果</h2>
            </div>
            <div className="metric-grid">
              <div>
                <span>章节数</span>
                <strong>{result.chapterCount}</strong>
              </div>
              <div>
                <span>文本字数</span>
                <strong>{result.wordCount}</strong>
              </div>
            </div>
            <p className={error ? "message error" : result.isValid ? "message success" : "message"}>
              {error || result.message}
            </p>
            {generationMessage ? <p className="message success">{generationMessage}</p> : null}
            <div className="chapter-list">
              {result.chapters.map((chapter) => (
                <article key={chapter.chapter_id} className="chapter-card">
                  <div>
                    <strong>{chapter.title}</strong>
                    <span>{chapter.word_count} 字</span>
                  </div>
                  <p>{chapter.preview || "该章节暂无正文预览"}</p>
                </article>
              ))}
            </div>
          </section>
          </div>
        ) : (
          <div className="layout-grid">
            <section className="input-panel">
              <div className="panel-heading">
                <FileText size={20} />
                <h2>YAML 文本</h2>
              </div>
              <textarea
                value={yamlText}
                onChange={(event) => setYamlText(event.target.value)}
                placeholder="请粘贴剧本 YAML，用于检查是否符合 schemas/script.schema.yaml"
                spellCheck={false}
              />
              <div className="actions">
                <button className="secondary-button" onClick={handleLoadSampleYaml} disabled={isValidatingYaml}>
                  <BookOpen size={18} />
                  加载示例 YAML
                </button>
                <button className="primary-button" disabled={!canValidateYaml} onClick={handleValidateYaml}>
                  {isValidatingYaml ? <Loader2 className="spin" size={18} /> : <CheckCircle2 size={18} />}
                  校验 YAML
                </button>
                <button className="secondary-button" disabled={!yamlText.trim()} onClick={handleExportYaml}>
                  <Download size={18} />
                  导出 YAML
                </button>
                <button className="secondary-button" onClick={handleResetYaml}>
                  <RotateCcw size={18} />
                  清空
                </button>
              </div>
            </section>

            <section className="result-panel">
              <div className="panel-heading">
                <CheckCircle2 size={20} />
                <h2>Schema 校验结果</h2>
              </div>
              <div className="metric-grid">
                <div>
                  <span>是否可解析</span>
                  <strong>{yamlResult.is_parseable ? "是" : "否"}</strong>
                </div>
                <div>
                  <span>Schema 状态</span>
                  <strong>{yamlResult.is_valid ? "通过" : "未通过"}</strong>
                </div>
                <div>
                  <span>人物数</span>
                  <strong>{yamlResult.summary.character_count}</strong>
                </div>
                <div>
                  <span>场景数</span>
                  <strong>{yamlResult.summary.scene_count}</strong>
                </div>
              </div>
              <p className={yamlError ? "message error" : yamlResult.is_valid ? "message success" : "message"}>
                {yamlError || yamlResult.message}
              </p>
              <div className="field-list">
                {yamlResult.top_level_fields.map((field) => (
                  <span key={field}>{field}</span>
                ))}
              </div>
              <div className="error-list">
                {yamlResult.errors.map((validationError) => (
                  <p key={validationError}>{validationError}</p>
                ))}
              </div>
              <StickmanSceneDemo scenes={yamlResult.scenes_preview} />
              <div className="preview-section">
                <div className="panel-heading compact-heading">
                  <h2>人物表</h2>
                </div>
                <div className="character-grid">
                  {yamlResult.characters_preview.map((character) => (
                    <article key={character.name} className="preview-card">
                      <div>
                        <strong>{character.name}</strong>
                        <span>{character.role}</span>
                      </div>
                      <p>{character.description || "暂无人物说明"}</p>
                      <div className="tag-row">
                        {character.traits.map((trait) => (
                          <span key={trait}>{trait}</span>
                        ))}
                      </div>
                    </article>
                  ))}
                </div>
              </div>
              <div className="preview-section">
                <div className="panel-heading compact-heading">
                  <h2>场景卡片</h2>
                </div>
                <div className="scene-grid">
                  {yamlResult.scenes_preview.map((scene) => (
                    <article key={scene.scene_id} className="preview-card">
                      <div>
                        <strong>{scene.scene_id}</strong>
                        <span>{scene.source_chapter}</span>
                      </div>
                      <p>{scene.location} / {scene.time}</p>
                      <p>{scene.summary || "暂无场景摘要"}</p>
                      <div className="tag-row">
                        {scene.characters_in_scene.map((character) => (
                          <span key={character}>{character}</span>
                        ))}
                        <span>{scene.dialogue_count} 句对白</span>
                      </div>
                    </article>
                  ))}
                </div>
              </div>
            </section>
          </div>
        )}
      </section>
    </main>
  );
}

export default App;

import { BookOpen, CheckCircle2, FileText, Loader2, RotateCcw, ScanText } from "lucide-react";
import { useMemo, useState } from "react";
import { parseChapters, validateYaml, type ChapterPreview, type ValidateYamlData } from "./services/api";

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
  top_level_fields: []
};

type WorkMode = "novel" | "yaml";

function App() {
  const [mode, setMode] = useState<WorkMode>("novel");
  const [novelText, setNovelText] = useState("");
  const [result, setResult] = useState<ValidationState>(EMPTY_RESULT);
  const [error, setError] = useState("");
  const [isChecking, setIsChecking] = useState(false);
  const [yamlText, setYamlText] = useState("");
  const [yamlResult, setYamlResult] = useState<ValidateYamlData>(EMPTY_YAML_RESULT);
  const [yamlError, setYamlError] = useState("");
  const [isValidatingYaml, setIsValidatingYaml] = useState(false);

  const canCheck = novelText.trim().length > 0 && !isChecking;
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
      setResult(EMPTY_RESULT);
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

  return (
    <main className="app-shell">
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
                <button className="primary-button" disabled={!canValidateYaml} onClick={handleValidateYaml}>
                  {isValidatingYaml ? <Loader2 className="spin" size={18} /> : <CheckCircle2 size={18} />}
                  校验 YAML
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
            </section>
          </div>
        )}
      </section>
    </main>
  );
}

export default App;

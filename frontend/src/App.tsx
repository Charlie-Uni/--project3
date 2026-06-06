import { FileText, Loader2, RotateCcw, ScanText } from "lucide-react";
import { useMemo, useState } from "react";
import { parseChapters, type ChapterPreview } from "./services/api";

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

function App() {
  const [novelText, setNovelText] = useState("");
  const [result, setResult] = useState<ValidationState>(EMPTY_RESULT);
  const [error, setError] = useState("");
  const [isChecking, setIsChecking] = useState(false);

  const canCheck = novelText.trim().length > 0 && !isChecking;

  const statusLabel = useMemo(() => {
    if (isChecking) return "校验中";
    if (error) return "校验失败";
    return result.isValid ? "可生成剧本" : "需要补充章节";
  }, [error, isChecking, result.isValid]);

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

  function handleReset() {
    setNovelText("");
    setResult(EMPTY_RESULT);
    setError("");
  }

  return (
    <main className="app-shell">
      <section className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">AI 小说转剧本工具</p>
            <h1>小说输入与章节校验</h1>
          </div>
          <div className={`status-pill ${result.isValid ? "valid" : "invalid"}`}>
            {statusLabel}
          </div>
        </header>

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
      </section>
    </main>
  );
}

export default App;

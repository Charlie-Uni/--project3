import { History, RotateCcw, Save, Trash2 } from "lucide-react";

export type ScriptHistoryItem = {
  id: string;
  title: string;
  savedAt: string;
  yamlText: string;
  characterCount: number;
  sceneCount: number;
  dialogueCount: number;
};

type ScriptHistoryPanelProps = {
  items: ScriptHistoryItem[];
  canSave: boolean;
  onSave: () => void;
  onRestore: (item: ScriptHistoryItem) => void;
  onDelete: (id: string) => void;
  onClear: () => void;
};

function formatSavedAt(savedAt: string) {
  const date = new Date(savedAt);
  if (Number.isNaN(date.getTime())) {
    return "未知时间";
  }
  return date.toLocaleString("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit"
  });
}

export function ScriptHistoryPanel({
  items,
  canSave,
  onSave,
  onRestore,
  onDelete,
  onClear
}: ScriptHistoryPanelProps) {
  return (
    <div className="preview-section history-section">
      <div className="history-heading">
        <div className="panel-heading compact-heading">
          <History size={18} />
          <h2>本地作品历史</h2>
        </div>
        <div className="history-actions">
          <button className="history-save-button" disabled={!canSave} onClick={onSave}>
            <Save size={15} />
            保存当前
          </button>
          <button className="history-clear-button" disabled={items.length === 0} onClick={onClear}>
            清空
          </button>
        </div>
      </div>

      {items.length === 0 ? (
        <div className="empty-state compact-empty">
          <p>暂无历史作品</p>
          <p className="empty-state-hint">生成或校验 YAML 后可保存到浏览器本地</p>
        </div>
      ) : (
        <div className="history-list">
          {items.map((item) => (
            <article key={item.id} className="history-card">
              <div className="history-card-main">
                <strong>{item.title}</strong>
                <span>{formatSavedAt(item.savedAt)}</span>
              </div>
              <div className="history-meta">
                <span>{item.characterCount} 人物</span>
                <span>{item.sceneCount} 场景</span>
                <span>{item.dialogueCount} 对白</span>
              </div>
              <div className="history-card-actions">
                <button onClick={() => onRestore(item)}>
                  <RotateCcw size={14} />
                  恢复
                </button>
                <button className="danger" onClick={() => onDelete(item.id)} aria-label={`删除 ${item.title}`}>
                  <Trash2 size={14} />
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}

# 最终交付物清单

## 交付物总览

| 交付物 | 文件或位置 | 对应评分点 |
|---|---|---|
| 项目代码 | `frontend/`、`backend/` | 作品完整度、开发过程与质量 |
| README | `README.md` | 演示与表达、可复现性 |
| YAML Schema 文档 | `docs/schema-design.md` | 作品完整度、工程规范 |
| YAML Schema 实体 | `schemas/script.schema.yaml` | Schema 校验硬指标 |
| 示例小说文本 | `examples/sample_novel.txt` | demo 稳定性 |
| 示例 YAML 输出 | `examples/sample_output.yaml` | YAML 输出要求、Schema 校验 |
| Prompt 模板 | `prompts/` | AI 转换逻辑可解释性 |
| AI 转换说明 | `docs/ai-conversion.md` | 产品设计、技术表达 |
| 工程骨架说明 | `docs/engineering-skeleton.md` | 架构清晰度、协作规范 |
| 后端测试 | `tests/backend/` | 开发过程与质量 |
| Demo 检查清单 | `docs/demo-checklist.md` | 演示与表达 |
| 环境变量示例 | `.env.example` | API Key 安全 |
| 忽略规则 | `.gitignore` | 仓库安全规范 |
| PR 记录 | GitHub Pull Requests | 开发过程真实性 |
| commit 记录 | GitHub Commits | 持续开发过程 |

## 作品完整度与创新性

- 输入小说并校验章节数。
- 支持 3 章以上小说文本。
- AI 生成结构化 YAML 剧本。
- YAML 可编辑、可校验、可导出。
- 展示人物表、场景卡片和剧本统计。
- 支持 mock 兜底，保证 demo 稳定。

## 开发过程与质量

- 前后端分层。
- Prompt 独立管理。
- Schema 独立管理。
- API Key 只通过后端环境变量读取。
- 后端核心流程有 pytest 测试。
- commit 使用中文 Conventional Commits。
- 每个 PR 聚焦单一功能。

## 演示与表达

推荐演示顺序：

1. 打开前端页面。
2. 加载示例小说。
3. 校验章节数量。
4. 生成 YAML 剧本。
5. 展示 Schema 校验结果。
6. 展示人物表和场景卡片。
7. 编辑 YAML 并重新校验。
8. 导出 YAML。
9. 展示 `docs/schema-design.md`。
10. 展示 GitHub PR 和 commit 记录。

## 最终自检命令

后端测试：

```bash
.venv/bin/python -m pytest
```

前端构建：

```bash
cd frontend
npm run build
```

Git 状态：

```bash
git status --short
```

确认不要提交：

```text
.env
node_modules/
.venv/
dist/
```

## 建议 PR 顺序

1. `feat: 添加剧本 YAML Schema 与输出样例`
2. `feat: 添加小说转剧本 Prompt 体系`
3. `chore: 添加项目工程骨架配置`
4. `feat: 添加小说输入与章节校验`
5. `feat: 添加 YAML Schema 校验功能`
6. `feat: 添加 AI 剧本生成接口`
7. `feat: 添加剧本生成预览与导出`
8. `feat: 添加人物场景预览面板`
9. `test: 添加核心后端流程测试`
10. `docs: 添加最终交付与演示文档`

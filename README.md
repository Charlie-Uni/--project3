# AI 小说转剧本工具

AI 小说转剧本工具用于将 3 章以上小说文本转换为结构化剧本 YAML 初稿。系统支持章节校验、AI 剧本生成、YAML Schema 校验、人物与场景预览、火柴人场景演示、YAML 编辑和导出。

项目核心目标是把非结构化小说改编流程做成可验证的工程闭环：

```text
输入小说 → 章节校验 → AI 生成 YAML → Schema 校验 → 预览演示 → 编辑导出
```

## 功能亮点

- 支持粘贴小说文本或上传 `.txt` 小说文件。
- 支持识别 3 章以上小说文本，兼容 `第1章`、`Chapter 1`、`## 第1章` 等标题格式。
- 支持 OpenAI GPT、Gemini、DeepSeek 三种模型提供商选择。
- API Key 只通过后端环境变量读取，前端不接触密钥。
- 输出结构化 YAML 剧本初稿。
- 使用 `schemas/script.schema.yaml` 做 YAML Schema 校验。
- 支持人物表、场景卡片、冲突、动作、对白、旁白、情绪和转场预览。
- 支持独立场景演示页，用火柴人片段展示 YAML 场景内容。
- 支持 YAML 编辑和导出。
- 默认 `USE_MOCK_AI=true`，保证 demo 稳定可复现。

## 技术栈

| 层级 | 技术 |
|---|---|
| 前端 | React、Vite、TypeScript、lucide-react |
| 后端 | FastAPI、Python |
| AI 调用 | OpenAI Python SDK，兼容 OpenAI 格式接口 |
| YAML 处理 | PyYAML |
| Schema 校验 | jsonschema |
| 配置管理 | python-dotenv、`.env` |
| 测试 | pytest |
| 示例数据 | `examples/`、`frontend/public/` |

## 项目结构

```text
frontend/       前端页面、上传、预览、场景演示
backend/        后端 API、AI 调用、章节解析、YAML 校验
prompts/        小说转剧本 Prompt 模板
schemas/        剧本 YAML Schema
docs/           Schema、AI 转换和工程设计文档
examples/       示例小说文本和示例 YAML 输出
tests/          后端核心流程测试
```

## 快速开始

### 1. 安装后端依赖

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### 2. 安装前端依赖

```bash
cd frontend
npm install
cd ..
```

### 3. 配置环境变量

```bash
cp .env.example .env
```

推荐 demo 配置：

```env
USE_MOCK_AI=true
DEFAULT_AI_PROVIDER=openai
```

如果要调用真实 OpenAI：

```env
USE_MOCK_AI=false
DEFAULT_AI_PROVIDER=openai
OPENAI_API_KEY=你的_OpenAI_API_Key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

如果要调用 Gemini 或 DeepSeek，只需要在 `.env` 中配置对应 provider 的 API Key、base url 和 model。不要提交 `.env`。

### 4. 启动后端

```bash
source .venv/bin/activate
.venv/bin/uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

健康检查：

```text
http://127.0.0.1:8000/api/health
```

接口文档：

```text
http://127.0.0.1:8000/docs
```

### 5. 启动前端

另开一个终端：

```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

前端页面：

```text
http://127.0.0.1:5173/
```

## Demo 视频

Demo 视频链接已放到 README，可直接在线观看，无需下载或注册网盘。

B 站在线观看：

```text
https://www.bilibili.com/video/BV1UXEx6qEPm/
```

百度网盘备用链接：

```text
https://pan.baidu.com/s/1eAHYJBm45qj5ti3L8HV5AA?pwd=4rm7
```

提取码：

```text
4rm7
```

## 测试方式

后端测试：

```bash
.venv/bin/python -m pytest
```

前端构建：

```bash
cd frontend
npm run build
```

当前测试覆盖：

- 章节解析。
- 少于 3 章文本的拦截。
- YAML Schema 校验。
- AI 生成接口 mock 模式。
- 多模型 provider 参数。
- 缺少 API Key 的错误提示。
- 场景预览字段提取。

## YAML 输出与 Schema

示例输出：

```text
examples/sample_output.yaml
```

Schema 实体：

```text
schemas/script.schema.yaml
```

Schema 设计文档：

```text
docs/schema-design.md
```

核心顶层字段：

```text
metadata
source_info
characters
chapters
script
global_notes
```

场景字段覆盖：

```text
scene_id
source_chapter
location
time
characters_in_scene
summary
conflicts
plot_points
actions
dialogues
narration
emotions
transitions
notes
```

## 安全说明

- 真实 API Key 只放在本地 `.env`。
- `.env` 已被 `.gitignore` 忽略。
- `.env.example` 只能放占位符。
- 前端只传 provider，不传 API Key。
- 后端通过环境变量读取对应模型密钥。
- 如果 API Key 曾经出现在公开仓库中，应立即撤销并重新生成。

## PR 与 Commit 规范

commit 使用中文 Conventional Commits，例如：

```text
feat: 添加小说文件上传功能
feat: 添加多模型提供商选择
fix: 修复章节标题解析规则
style: 优化前端工作台布局
test: 添加 YAML 校验测试
docs: 更新 README 使用说明
```

PR 要求：

- 每个 PR 只做一件事。
- 大功能拆成多个小 PR。
- PR 描述包含功能描述、实现思路、测试方式和合并要求。
- 合并后 `main` 应保持可运行。

## 未来扩展

- 本地作品历史记录。
- 剧本质量评分面板。
- YAML 自动修复按钮。
- 更多剧本风格选择。
- 导出 Markdown 或 PDF 剧本预览。

# AI 小说转剧本工具

## 项目简介

AI 小说转剧本工具用于将 3 章以上小说文本转换为结构化剧本 YAML 初稿。系统支持小说章节校验、AI 生成剧本 YAML、YAML Schema 校验、人物与场景预览、YAML 编辑和导出。

项目重点不是简单生成文本，而是把小说改编流程拆成可验证的工程闭环：

```text
输入小说 → 章节数校验 → AI 生成 YAML → Schema 校验 → 人物场景预览 → 编辑 → 导出
```

## 功能亮点

- 支持 3 章以上小说文本输入和章节数量校验
- 后端调用 AI，API Key 不暴露到前端
- 输出结构化 YAML 剧本初稿
- 使用 `schemas/script.schema.yaml` 进行 Schema 校验
- 支持人物表、场景卡片和剧本统计预览
- 支持 YAML 编辑和导出
- 支持 `USE_MOCK_AI=true` 示例兜底，保证 demo 稳定

## 技术栈

| 层级 | 技术 |
|---|---|
| 前端 | React + Vite + TypeScript |
| 后端 | FastAPI + Python |
| AI 调用 | OpenAI Python SDK，支持 OpenAI 兼容接口 |
| YAML 处理 | PyYAML |
| Schema 校验 | jsonschema |
| 测试 | pytest |
| 示例数据 | examples/ |

## 项目结构

```text
frontend/       前端页面和 API 请求
backend/        后端接口、AI 调用和校验服务
prompts/        小说转剧本 Prompt 模板
schemas/        剧本 YAML Schema
docs/           Schema、工程设计和交付文档
examples/       示例小说和示例 YAML
tests/          后端测试用例
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

如果先用示例数据跑 demo，保持：

```env
USE_MOCK_AI=true
```

如果要调用真实 AI，把 `.env` 改成：

```env
OPENAI_API_KEY=你的真实_API_Key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
USE_MOCK_AI=false
```

如果使用 Gemini OpenAI 兼容接口，可改为：

```env
OPENAI_API_KEY=你的_Gemini_API_Key
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
OPENAI_MODEL=你的_Gemini_模型名
USE_MOCK_AI=false
```

不要提交 `.env`。

### 4. 启动后端

```bash
export $(grep -v '^#' .env | xargs)
.venv/bin/uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

后端接口文档：

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

## 使用流程

1. 点击“加载示例”
2. 点击“校验章节”
3. 章节数量满足 3 章后点击“生成剧本 YAML”
4. 系统切换到 YAML Schema 校验页
5. 查看人物表、场景卡片和统计信息
6. 可以编辑 YAML
7. 点击“校验 YAML”
8. 点击“导出 YAML”

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

- 章节解析
- 少于 3 章输入
- YAML Schema 校验
- AI 生成接口 mock 模式
- 缺少 API Key 的错误提示

## 安全说明

- 真实 API Key 只放在本地 `.env`
- `.env` 已被 `.gitignore` 忽略
- 前端不读取 API Key
- AI 调用只通过后端完成
- 如果 API Key 误传到公开仓库，应立即撤销并重新生成

## 主要文档

- [YAML Schema 设计文档](docs/schema-design.md)
- [AI 转换逻辑与 Prompt](docs/ai-conversion.md)
- [工程骨架设计](docs/engineering-skeleton.md)

## 示例文件

- [示例小说](examples/sample_novel.txt)
- [示例 YAML 输出](examples/sample_output.yaml)
- [剧本 YAML Schema](schemas/script.schema.yaml)

## PR 与 commit 规范

commit 使用中文 Conventional Commits，例如：

```text
feat: 添加章节数量校验接口
feat: 添加 YAML Schema 校验接口
test: 添加 AI 剧本生成接口测试
docs: 添加本地运行说明
```

PR 要求：

- 每个 PR 只做一件事
- 大功能拆成多个小 PR
- PR 描述包含功能描述、实现思路、测试方式和合并要求
- 主分支合并后保持可运行

## 未来改进方向

- 支持真实长篇小说分段处理
- 增加更多剧本风格选项
- 增加 YAML 自动修复前端按钮
- 支持历史记录保存
- 支持导出 Markdown 或 PDF 剧本预览

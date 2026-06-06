# 工程骨架设计

## 1. 技术栈

判断标准只有一个: 3 天内能不能稳。

| 环节 | 推荐栈 | 推荐理由 | 备选栈 | 备选理由 |
|---|---|---|---|---|
| 前端 | React + Vite + TypeScript | 启动快，生态成熟，适合快速做输入、预览、编辑、导出页面 | Vue 3 + Vite | 如果团队更熟 Vue，开发效率更高 |
| UI 组件 | Tailwind CSS + shadcn/ui | 适合快速做干净的课程项目界面，组件可控 | Ant Design | 后台管理风格更完整，表单和提示组件成熟 |
| YAML 编辑 | textarea 起步，后续可换 CodeMirror | textarea 最稳，3 天内不会卡在编辑器集成 | CodeMirror | 代码高亮和编辑体验更好，作为加分项 |
| 后端 | FastAPI + Python | AI 调用、YAML 解析、Schema 校验实现快 | Node.js + Express | 如果团队全员熟 JavaScript，可统一语言 |
| AI 调用方式 | 后端调用 OpenAI 兼容接口 | API Key 只在后端读取，安全，符合公开仓库要求 | 本地 mock 示例输出 | AI API 不稳定时保证 demo 可复现 |
| YAML 生成 | PyYAML | 简单稳定，适合对象和 YAML 互转 | ruamel.yaml | 更适合保留注释和顺序，但学习成本略高 |
| YAML 校验 | jsonschema | 可直接校验 YAML 解析后的 dict，和 Schema 文件配合清楚 | Pydantic | 适合写 Python 数据模型，但 Schema 文档联动稍弱 |
| 存储 | 本地 examples/ 和 outputs/ 文件 | 3 天项目最稳，方便评委查看输入输出样例 | SQLite | 如果要做历史记录，可轻量加入 |
| 文件上传 | FastAPI UploadFile | 支持上传 txt 小说，实现简单 | 仅支持粘贴文本 | 时间不够时降级，仍满足核心要求 |
| 文件导出 | 前端 Blob 下载 YAML | 不依赖复杂后端文件服务，demo 稳定 | 后端生成文件流下载 | 适合后端统一管理导出文件 |
| 本地运行 | 前端 Vite + 后端 uvicorn | 开发和评审复现都简单 | docker-compose | 环境更统一，但配置成本更高 |
| 环境变量 | backend .env + .env.example + python-dotenv | API Key 不进前端，不进仓库，符合安全规范 | 系统环境变量 | 部署时更安全，但本地教学不够直观 |
| 部署方式 | 前端 Vercel，后端 Render 或 Railway | 免费方案多，演示方便 | 仅本地运行 | 3 天时间紧时更稳，README 写清即可 |
| 测试 | pytest + jsonschema 校验测试 | 快速覆盖章节校验、YAML 解析、Schema 校验 | Vitest + pytest | 前端逻辑较多时增加前端测试 |

## 2. 推荐目录结构

```text
ai-novel-to-script/
  frontend/
    src/
      components/
      pages/
      services/
      types/
      App.tsx
      main.tsx
    package.json
    vite.config.ts

  backend/
    app/
      api/
        generate_script.py
      services/
      main.py
    requirements.txt

  prompts/
    system_prompt.txt
    user_prompt_template.txt
    yaml_fix_prompt.txt
    schema_retry_prompt.txt
    chapter_summary_prompt.txt
    character_prompt.txt
    scene_split_prompt.txt

  schemas/
    script.schema.yaml

  docs/
    schema-design.md
    ai-conversion.md
    engineering-skeleton.md

  examples/
    sample_novel.txt
    sample_output.yaml

  tests/
    backend/
      test_chapter_parser.py
      test_yaml_validation.py

  .env.example
  .gitignore
  README.md
```

| 目录 | 作用 |
|---|---|
| frontend/ | 前端页面、组件、API 请求、类型定义 |
| backend/ | 后端接口、AI 调用、YAML 解析、Schema 校验 |
| prompts/ | 集中管理所有 Prompt，避免写死在业务代码里 |
| schemas/ | 存放 YAML Schema，供后端校验和文档引用 |
| docs/ | Schema 设计、AI 转换逻辑、工程骨架等项目文档 |
| examples/ | 示例小说输入和示例 YAML 输出，保障 demo 稳定 |
| tests/ | 章节解析、YAML 校验、接口核心逻辑测试 |

## 3. PR 拆分方案

| PR | 标题 | 单一事项 | commit message | 评分价值 |
|---|---|---|---|---|
| PR-1 | feat: 添加剧本 YAML Schema 与输出样例 | 建立 YAML 输出样例、Schema 实体和设计文档 | `feat: 添加剧本 YAML 输出样例`<br>`feat: 添加剧本 YAML Schema`<br>`docs: 添加 YAML Schema 设计文档` | 满足 YAML 输出和 Schema 文档硬性要求 |
| PR-2 | feat: 添加小说转剧本 Prompt 体系 | 增加转换逻辑文档和 7 个 Prompt 模板 | `docs: 添加 AI 转换逻辑说明`<br>`feat: 添加小说转剧本 Prompt 模板` | 体现 AI 转换流程可解释、可实现 |
| PR-3 | chore: 添加项目工程骨架配置 | 增加 .gitignore、.env.example 和后端接口骨架 | `chore: 添加仓库忽略规则`<br>`chore: 添加环境变量示例文件`<br>`feat: 添加后端 AI 生成接口骨架`<br>`docs: 添加工程骨架设计文档` | 体现安全规范、工程分层和主分支可持续演进 |
| PR-4 | feat: 添加小说输入与章节校验 | 前端输入区和后端章节数量校验 | `feat: 添加小说文本输入组件`<br>`feat: 添加示例小说加载入口`<br>`feat: 添加章节数量解析服务`<br>`fix: 处理空文本输入提示` | 对应至少 3 章输入的硬性要求 |
| PR-5 | feat: 添加 YAML 生成与 Schema 校验链路 | 串联 AI 输出、YAML 解析、Schema 校验和失败重试 | `feat: 添加 AI 剧本生成接口`<br>`feat: 添加 YAML 解析服务`<br>`feat: 添加 Schema 校验失败重试流程`<br>`fix: 返回可读的校验错误信息` | 开发过程 40% 中最容易被评委验证的硬指标 |
| PR-6 | feat: 添加 YAML 预览编辑与导出 | 前端展示、编辑、重新校验和下载 YAML | `feat: 添加 YAML 预览面板`<br>`feat: 添加 YAML 编辑功能`<br>`feat: 添加 YAML 导出功能` | 形成输入到导出的完整产品闭环 |
| PR-7 | feat: 添加人物与场景预览 | 人物表、场景卡片和生成结果统计 | `feat: 添加人物表预览`<br>`feat: 添加场景卡片预览`<br>`feat: 添加生成结果统计面板` | 提升作品创新性和 demo 表达效果 |
| PR-8 | docs: 完成测试文档与演示整理 | 补测试说明、运行说明、示例数据和最终演示材料 | `test: 添加 YAML Schema 校验用例`<br>`test: 添加章节解析测试用例`<br>`docs: 添加本地运行说明`<br>`docs: 添加最终演示检查清单` | 保证评委能运行主分支并复现 demo |

## 4. 20 个 commit message 示例

```text
chore: 添加仓库忽略规则
chore: 添加环境变量示例文件
chore: 初始化前后端目录结构
feat: 添加剧本 YAML 输出样例
feat: 添加剧本 YAML Schema
docs: 添加 YAML Schema 设计文档
docs: 添加 AI 转换逻辑说明
feat: 添加小说转剧本 Prompt 模板
feat: 添加后端 AI 生成接口骨架
feat: 添加小说文本输入组件
feat: 添加示例小说加载入口
feat: 添加章节数量解析服务
fix: 处理空文本输入提示
feat: 添加 AI 剧本生成接口
feat: 添加 YAML 解析服务
feat: 添加 Schema 校验失败重试流程
fix: 返回可读的校验错误信息
feat: 添加 YAML 预览面板
feat: 添加 YAML 编辑功能
feat: 添加 YAML 导出功能
```

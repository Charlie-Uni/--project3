# Demo 检查清单

## 录制前检查

- 后端已启动: `http://127.0.0.1:8000/docs`
- 前端已启动: `http://127.0.0.1:5173/`
- `.env` 已配置，且未提交到 Git
- demo 稳定优先使用 `USE_MOCK_AI=true`
- 真实 API 演示时再切换 `USE_MOCK_AI=false`
- `examples/sample_novel.txt` 可正常加载
- `examples/sample_output.yaml` 可通过 Schema 校验
- `npm run build` 已通过
- `.venv/bin/python -m pytest` 已通过

## 3 到 5 分钟演示路径

1. 简短介绍项目目标: 小说转结构化剧本 YAML。
2. 展示首页，说明当前闭环。
3. 点击“加载示例”。
4. 点击“校验章节”，展示 3 章校验通过。
5. 点击“生成剧本 YAML”。
6. 切到 YAML 页面，展示 Schema 校验通过。
7. 展示顶层字段、人物数、场景数。
8. 展示人物表卡片。
9. 展示场景卡片。
10. 手动改坏一处 YAML，点击“校验 YAML”，展示错误提示。
11. 恢复或重新加载示例 YAML，展示校验通过。
12. 点击“导出 YAML”。
13. 打开 `docs/schema-design.md`，展示字段说明。
14. 打开 GitHub，展示 PR 和 commit 历史。
15. 总结亮点和后续扩展。

## 重点表达句

- 本项目不是直接让 AI 写一段剧本，而是把小说改编拆成可校验的结构化流程。
- 生成结果必须是 YAML，并且会通过 Schema 校验。
- Prompt、Schema、示例数据、测试和 API Key 管理都独立分层。
- 即使真实 AI API 不稳定，也可以用 mock 示例保证 demo 可复现。
- 评委可以通过测试和 PR 历史验证开发过程不是一次性堆代码。

## 不建议浪费时间讲的内容

- 不详细解释每一行 Prompt。
- 不现场讲完整 Schema 的所有字段。
- 不展示复杂环境安装过程。
- 不现场注册 API Key。
- 不演示和评分无关的 Git 操作细节。

## 失败兜底

| 问题 | 处理方式 |
|---|---|
| AI API 调用失败 | 设置 `USE_MOCK_AI=true` 并重启后端 |
| 8000 端口被占用 | 用 `lsof -i :8000` 找 PID，然后 `kill PID` |
| 前端未显示页面 | 确认打开的是 `http://127.0.0.1:5173/` |
| YAML 校验失败 | 点击“加载示例 YAML”恢复稳定样例 |
| 生成按钮不可用 | 先点击“校验章节”，确保章节数不少于 3 |

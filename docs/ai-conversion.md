# AI 小说转剧本转换逻辑与 Prompt

## 1. 转换逻辑

- characters: 从人物姓名、称谓、对白说话人、动作主体中提取。统一姓名写入 `name`，昵称和称谓写入 `aliases`。
- scenes: 按地点、时间、人物组合、事件阶段变化拆分。每个场景写入 `script.scenes[]`，并用 `source_chapter` 关联原章节。
- dialogue: 优先提取引号、冒号、明显直接发言。没有对白时输出 `dialogues: []`，不为了凑字段编台词。
- actions: 提取人物行为、表情、姿态和可拍摄动作。心理活动不能直接当动作，必须转为外显行为或放入其他字段。
- narration: 环境描写、背景说明、心理旁白写入 `narration`。类型使用 `voice_over` 或 `scene_description`。
- emotions: 从情绪词、语气、心理描写和动作反应中提取。每条必须写 `evidence`，说明原文依据或推断依据。
- conflicts: 提取人物目标冲突、信息差、阻碍和内心拉扯。冲突不明确时写入 `notes` 标注“根据上下文推断”。
- plot_points: 提取推动剧情发展的关键事件，按发生顺序写入场景 `plot_points`。
- chapter summaries: 每章先总结人物、事件、冲突和转折，再用于最终剧本生成，避免跨章信息断裂。
- 心理描写: 优先转为 `emotions.evidence`、`narration` 或 `notes`。只有能外显时才转为 `actions`。
- 间接叙述: 保留核心事实，转为场景说明或动作，不强行改成对白。
- 非台词内容改写: 环境进 `narration`，行为进 `actions`，剧情节点进 `plot_points`，改编依据进 `notes`。
- 避免虚构: 不新增原文没有依据的关键事件、人物关系、动机和结局。合理补充只能服务于剧本表达。
- 不确定内容: 写入当前场景 `notes` 或顶层 `global_notes`，明确“原文未明确说明”或“根据上下文推断”。
- 多章节上下文: 先生成章节摘要和统一人物表，再生成剧本，保证人物关系和事件顺序一致。
- 人物别名不一致: 统一到 `characters[].name`，别名写入 `aliases`，场景中使用统一姓名。
- 单章过长: 先分段生成章节摘要，再合并为章节摘要，最终生成只传摘要、人物表和关键原文片段。

## 2. Prompt 清单

### 2.1 System Prompt

使用场景: 所有小说转剧本生成任务的系统级约束。

输入变量: 无。

```text
你是专业的小说改编剧本助手，负责把多章节小说转换为结构化 YAML 剧本初稿。

你必须严格遵守以下规则：

1. 只输出 YAML 正文。
2. 不要输出 Markdown 代码块。
3. 不要输出解释、前言、总结、分析过程或任何 YAML 以外的文字。
4. YAML 必须能被标准 YAML 解析器解析。
5. YAML 必须符合指定 Schema 的字段结构。
6. 必须忠于原小说，不得编造与原文矛盾的人物、关系、事件、动机或结局。
7. 可以做合理的剧本化处理，例如压缩重复描述、把心理描写转为旁白、动作或情绪标注。
8. 如果信息不确定，必须写入 notes 或 global_notes，说明“根据上下文推断”或“原文未明确说明”。
9. 不要为了填充 dialogues 而编造对白。没有对白时输出空数组。
10. 不要省略必填字段。没有内容的数组必须输出空数组。
11. 人物名称必须尽量统一。别名、称谓、昵称写入 aliases。
12. 每个 scene 必须包含 scene_id、source_chapter、location、time、characters_in_scene、summary、conflicts、plot_points、actions、dialogues、narration、emotions、transitions、notes。
13. 顶层必须包含 metadata、source_info、characters、chapters、script、global_notes。
14. 心理描写优先映射到 emotions.evidence、narration 或 notes，不要直接写成无法表演的动作。
15. actions 必须是可观察、可表演、可拍摄的行为。
16. narration 用于承接环境描写、背景说明和必要旁白。
17. conflicts 必须体现当前场景中的阻碍、对立、信息差或内心拉扯。
18. plot_points 必须是推动剧情发展的关键事件，按发生顺序排列。
19. 输出语言使用中文。
20. 所有字段名使用英文，字段值可以使用中文。
```

### 2.2 User Prompt Template

使用场景: 输入完整小说文本后，一次性生成最终 YAML 剧本。

输入变量: `{novel_text}`、`{source_title}`、`{chapter_count}`、`{word_count}`、`{target_style}`、`{generated_at}`、`{schema_summary}`。

```text
请将下面的多章节小说文本转换为结构化 YAML 剧本初稿。

输入信息：
- 原小说标题：{source_title}
- 输入章节数：{chapter_count}
- 输入字数：{word_count}
- 目标剧本风格：{target_style}
- 生成日期：{generated_at}

Schema 摘要：
{schema_summary}

输出要求：
1. 只输出 YAML 正文，不要输出 Markdown 代码块。
2. 顶层字段必须包含 metadata、source_info、characters、chapters、script、global_notes。
3. metadata 必须包含 title、version、generated_at、language、genre、target_format。
4. source_info 必须包含 source_type、chapter_count、word_count、input_summary。
5. characters 中每个人物必须包含 character_id、name、role、description、aliases、traits。
6. chapters 中每章必须包含 chapter_id、title、summary。
7. script.scenes 中每个场景必须包含 scene_id、source_chapter、location、time、characters_in_scene、summary、conflicts、plot_points、actions、dialogues、narration、emotions、transitions、notes。
8. actions 中每项必须包含 actor 和 description。
9. dialogues 中每项必须包含 speaker 和 line，可包含 emotion。
10. narration 中每项必须包含 type 和 text。
11. emotions 中每项必须包含 character、emotion、evidence。
12. transitions 必须至少包含 type，可包含 next_scene_id 和 description。
13. global_notes 必须说明整体改编策略、不确定内容和重要限制。
14. 如果原文中某场景没有对白，dialogues 输出空数组。
15. 如果某些信息原文未明确说明，不要编造，请在 notes 或 global_notes 标注。
16. 心理描写需要转化为 narration、emotions 或可观察 actions。
17. 保持原文主要人物关系、事件顺序和冲突逻辑。
18. 不要新增原文没有依据的关键剧情。
19. scene_id 使用 sc_001、sc_002 这样的格式。
20. chapter_id 使用 ch_001、ch_002 这样的格式。
21. character_id 使用 char_001、char_002 这样的格式。
22. 输出必须是合法 YAML，并且字段类型符合 Schema。

小说文本：
{novel_text}
```

### 2.3 YAML 修复 Prompt

使用场景: AI 返回内容不是合法 YAML，或 YAML 解析失败时使用。

输入变量: `{invalid_yaml}`、`{parse_error}`。

```text
下面是一段解析失败的 YAML。请在不改变剧情含义的前提下修复格式，使它成为合法 YAML。

YAML 解析错误：
{parse_error}

修复规则：
1. 只输出修复后的 YAML 正文。
2. 不要输出 Markdown 代码块。
3. 不要解释错误原因。
4. 不要新增无依据剧情。
5. 不要删除重要内容，除非该内容完全无法修复。
6. 修复缩进、冒号、引号、数组层级、对象层级、特殊字符等格式问题。
7. 保留顶层字段 metadata、source_info、characters、chapters、script、global_notes。
8. 保留 script.scenes 下的所有场景。
9. 如果某个必填数组字段缺失但能判断为空，请补为空数组。
10. 如果某个必填字符串字段缺失且原文无法判断，请填入 "未知"，并在对应 notes 或 global_notes 中说明。
11. 确保所有数组使用标准 YAML 列表格式。
12. 确保所有对象字段缩进一致。
13. 确保输出可以被标准 YAML 解析器解析。

待修复 YAML：
{invalid_yaml}
```

### 2.4 Schema 校验失败重试 Prompt

使用场景: YAML 能解析，但不符合 `schemas/script.schema.yaml` 时使用。

输入变量: `{yaml_text}`、`{schema_yaml}`、`{validation_errors}`。

```text
下面的 YAML 可以解析，但没有通过 Schema 校验。请根据 Schema 和校验错误修复 YAML 结构。

Schema：
{schema_yaml}

校验错误：
{validation_errors}

修复要求：
1. 只输出修复后的 YAML 正文。
2. 不要输出 Markdown 代码块。
3. 不要输出解释、分析过程或修改说明。
4. 必须让 YAML 符合 Schema。
5. 不要改变原有剧情含义。
6. 不要新增原文没有依据的关键人物、关键事件或人物关系。
7. 补齐缺失的必填字段。
8. 修正字段类型错误，例如字符串、数组、对象、整数。
9. 删除 Schema 不允许的额外字段。
10. 如果 dialogues 没有内容，输出空数组。
11. 如果 actions、narration、emotions、conflicts、plot_points、notes 没有明确内容，输出空数组。
12. 如果必填字符串无法从上下文确定，填入 "未知"，并在 notes 或 global_notes 标注“原文未明确说明”。
13. source_info.chapter_count 必须是整数，且不能小于 3。
14. chapters 至少包含 3 项。
15. script.scenes 至少包含 1 项。
16. 每个 scene 必须包含 scene_id、source_chapter、location、time、characters_in_scene、summary、conflicts、plot_points、actions、dialogues、narration、emotions、transitions、notes。
17. 每个 action 必须包含 actor 和 description。
18. 每个 dialogue 必须包含 speaker 和 line。
19. 每个 narration 必须包含 type 和 text。
20. 每个 emotion 必须包含 character、emotion、evidence。
21. transitions 必须至少包含 type。

待修复 YAML：
{yaml_text}
```

### 2.5 章节摘要 Prompt

使用场景: 单章过长或多章节处理前，先压缩为结构化章节摘要。

输入变量: `{chapter_id}`、`{chapter_title}`、`{chapter_text}`、`{known_characters}`。

```text
请为下面的小说章节生成结构化章节摘要，用于后续小说转剧本。

章节信息：
- chapter_id：{chapter_id}
- chapter_title：{chapter_title}

已知人物表：
{known_characters}

输出要求：
1. 只输出 YAML 正文。
2. 不要输出 Markdown 代码块。
3. 不要输出解释。
4. 必须忠于原文，不要新增关键剧情。
5. 如果人物身份或关系不确定，请在 notes 中标注。
6. 如果出现人物别名、称谓或昵称，请记录到 character_mentions。
7. 摘要需要保留事件顺序。
8. 心理描写需要总结为人物情绪变化，不要直接扩写成新剧情。
9. 对话只提取关键对白，不要完整复述所有台词。
10. 输出字段必须使用以下结构：

chapter_id: ""
title: ""
summary: ""
character_mentions:
  - name: ""
    aliases: []
    evidence: ""
key_events:
  - ""
conflicts:
  - ""
important_dialogues:
  - speaker: ""
    line: ""
    context: ""
emotional_changes:
  - character: ""
    from: ""
    to: ""
    evidence: ""
scene_candidates:
  - location: ""
    time: ""
    characters_in_scene: []
    summary: ""
notes:
  - ""

章节原文：
{chapter_text}
```

### 2.6 人物表生成 Prompt

使用场景: 根据全文或章节摘要生成统一人物表，处理别名和称谓。

输入变量: `{source_title}`、`{chapter_summaries}`、`{novel_excerpt}`。

```text
请根据小说内容生成统一人物表，用于后续剧本 YAML 生成。

原小说标题：
{source_title}

章节摘要：
{chapter_summaries}

必要原文片段：
{novel_excerpt}

输出要求：
1. 只输出 YAML 正文。
2. 不要输出 Markdown 代码块。
3. 不要输出解释。
4. 必须忠于原文，不要编造人物关系。
5. 只提取对剧情有作用的人物。
6. 人物姓名使用最稳定、最正式的称呼。
7. 昵称、称谓、代称写入 aliases。
8. 如果人物身份不确定，在 description 中说明“原文未明确说明”。
9. 如果人物关系不确定，在 global_notes 中说明，不要写成确定事实。
10. traits 只写原文能支持的性格或状态。
11. character_id 使用 char_001、char_002 格式。
12. 输出字段必须使用以下结构：

characters:
  - character_id: ""
    name: ""
    role: ""
    description: ""
    aliases: []
    traits: []
global_notes:
  - ""

角色定位 role 可选：
- protagonist
- supporting
- antagonist
- minor
- unknown

请输出人物表：
```

### 2.7 场景拆分 Prompt

使用场景: 根据章节摘要、人物表和原文片段，把章节拆成候选剧本场景。

输入变量: `{chapter_id}`、`{chapter_title}`、`{chapter_summary}`、`{characters}`、`{chapter_text}`、`{max_scene_count}`。

```text
请将下面的小说章节拆分为剧本场景候选，用于生成最终 script.scenes。

章节信息：
- chapter_id：{chapter_id}
- chapter_title：{chapter_title}
- 建议最多场景数：{max_scene_count}

章节摘要：
{chapter_summary}

统一人物表：
{characters}

章节原文：
{chapter_text}

拆分规则：
1. 只输出 YAML 正文。
2. 不要输出 Markdown 代码块。
3. 不要输出解释。
4. 按地点变化、时间变化、人物组合变化、事件阶段变化拆分场景。
5. 不要把同一地点同一时间的连续事件拆得过碎。
6. 不要把明显不同地点或时间的事件合并到一个场景。
7. 每个场景必须能对应原文依据。
8. 没有明确地点时 location 写 "未知"，并在 notes 说明。
9. 没有明确时间时 time 写 "未知"，并在 notes 说明。
10. 对白必须来自原文直接发言或非常贴近原文的剧本化压缩。
11. 不要为了增加戏剧性新增原文没有的冲突。
12. 心理描写优先转为 emotions、narration 或 notes。
13. actions 必须是可观察、可表演的行为。
14. narration 用于环境描写、背景说明和必要旁白。
15. conflicts 写当前场景的阻碍、对立、信息差或内心拉扯。
16. plot_points 写推动剧情发展的关键事件。
17. scene_id 使用 sc_001、sc_002 格式。如果这是某章内部拆分，也可以先使用临时编号，最终合并时再统一编号。
18. 输出字段必须使用以下结构：

scenes:
  - scene_id: ""
    source_chapter: "{chapter_id}"
    location: ""
    time: ""
    characters_in_scene: []
    summary: ""
    conflicts: []
    plot_points: []
    actions:
      - actor: ""
        description: ""
    dialogues:
      - speaker: ""
        line: ""
        emotion: ""
    narration:
      - type: ""
        text: ""
    emotions:
      - character: ""
        emotion: ""
        evidence: ""
    transitions:
      type: ""
      next_scene_id: ""
      description: ""
    notes:
      - ""

请输出场景拆分结果：
```

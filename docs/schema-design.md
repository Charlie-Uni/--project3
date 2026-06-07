# YAML 剧本 Schema 设计文档

## 1. 设计目标

本 Schema 用于约束 AI 小说转剧本工具的 YAML 输出，目标是让生成结果同时满足三个要求：

1. 能表达小说改编后的剧本结构。
2. 能被程序解析和 Schema 校验。
3. 能被创作者继续编辑和打磨。

Schema 聚焦小说改编剧本初稿，不追求完整影视工业剧本格式。设计重点是字段稳定、层级清楚、适合 3 天课程项目落地和演示。

## 2. 顶层结构说明

| 顶层字段 | 类型 | 是否必填 | 说明 |
|---|---|---|---|
| metadata | object | 是 | 剧本元信息 |
| source_info | object | 是 | 原小说输入信息 |
| characters | array | 是 | 人物表 |
| chapters | array | 是 | 原小说章节摘要 |
| script | object | 是 | 剧本主体内容 |
| global_notes | array | 是 | 全局改编说明 |

## 3. Schema 设计原因

本 Schema 采用 `metadata`、`source_info`、`characters`、`chapters`、`script` 和 `global_notes` 六个顶层字段，是因为小说转剧本任务需要同时解决“来源可追踪、人物可整理、章节可映射、场景可编辑、改编依据可说明”这几个问题。

`metadata` 用于记录剧本标题、生成时间、语言和目标格式，方便导出、展示和版本管理。`source_info` 用于保留原小说的输入类型、章节数、字数和整体摘要，确保生成结果能追溯到原始文本，而不是脱离来源的普通 AI 文本。

`characters` 单独成表，是因为小说中的人物常常存在别名、称谓不一致和关系不清的问题。通过 `character_id`、`name`、`aliases`、`role` 和 `traits`，系统可以把人物信息整理成可复用的数据结构，方便场景引用、人物表展示和后续人工修改。

`chapters` 保留原小说章节结构，是为了满足“至少 3 章以上小说文本”的题目要求，也为了让每个剧本场景能通过 `source_chapter` 追踪来源章节。这样评委和作者可以看到剧本不是凭空生成，而是从原小说章节中拆解和改编得到的。

`script.scenes` 是剧本主体，因为剧本创作的基本单位是场景。每个 scene 下拆分 `location`、`time`、`characters_in_scene`、`summary`、`conflicts`、`plot_points`、`actions`、`dialogues`、`narration`、`emotions`、`transitions` 和 `notes`，是为了把小说中的环境描写、动作描写、直接对白、心理描写、情绪变化和情节推进转成可编辑、可校验、可继续打磨的剧本初稿。

`notes` 和 `global_notes` 用于记录改编说明和不确定内容。这样可以要求 AI 在信息不确定时做标注，而不是随意编造剧情，也方便作者后续判断哪些内容需要人工确认。

整体设计的核心原因是：小说是连续叙事文本，剧本是结构化场景文本。本 Schema 通过固定字段和类型约束，把非结构化小说拆解为人物、章节、场景、动作、对白、旁白、情绪和转场，使 AI 输出既能被程序校验，也能被创作者继续编辑。

## 4. 字段说明表

| 字段名 | 类型 | 是否必填 | 说明 | 设计原因 |
|---|---|---|---|---|
| metadata | object | 是 | 剧本标题、版本、语言、类型等元信息 | 方便识别和版本管理 |
| metadata.title | string | 是 | 剧本标题 | 便于展示和导出命名 |
| metadata.version | string | 是 | Schema 或结果版本 | 支持后续迭代 |
| metadata.generated_at | string | 是 | 生成日期 | 方便追踪生成时间 |
| metadata.language | string | 是 | 输出语言 | 支持中文和未来多语言 |
| metadata.genre | string | 否 | 剧本类型 | 支持风格化展示 |
| metadata.target_format | string | 是 | 目标输出格式 | 明确当前是剧本 YAML |
| source_info | object | 是 | 原小说来源信息 | 保留输入上下文 |
| source_info.source_type | string | 是 | 来源类型，当前通常为 novel | 支持未来扩展其他文本来源 |
| source_info.chapter_count | integer | 是 | 输入章节数，最小为 3 | 对应题目硬性要求 |
| source_info.word_count | integer | 否 | 输入字数 | 便于统计和调试 |
| source_info.input_summary | string | 否 | 输入小说整体摘要 | 方便快速理解原文 |
| characters | array | 是 | 人物列表 | 剧本改编必须先明确人物 |
| characters[].character_id | string | 是 | 人物唯一 ID | 方便程序引用 |
| characters[].name | string | 是 | 人物名称 | 剧本展示核心字段 |
| characters[].role | string | 是 | 人物定位 | 区分主角、配角等 |
| characters[].description | string | 否 | 人物简介 | 帮助理解角色 |
| characters[].aliases | array | 否 | 人物别名或称谓 | 处理小说中称谓不一致问题 |
| characters[].traits | array | 否 | 性格标签 | 支持人物表展示 |
| chapters | array | 是 | 原小说章节摘要列表，至少 3 项 | 保留小说章节来源 |
| chapters[].chapter_id | string | 是 | 章节 ID | 供 scene.source_chapter 引用 |
| chapters[].title | string | 是 | 章节标题 | 保留原文结构 |
| chapters[].summary | string | 是 | 章节摘要 | 支持多章节上下文理解 |
| script | object | 是 | 剧本主体 | 承载最终改编结果 |
| script.scenes | array | 是 | 场景列表 | 剧本的核心组织单位 |
| script.scenes[].scene_id | string | 是 | 场景 ID | 方便定位和跳转 |
| script.scenes[].source_chapter | string | 是 | 来源章节 ID | 保留小说到剧本的映射关系 |
| script.scenes[].location | string | 是 | 场景地点 | 剧本基本要素 |
| script.scenes[].time | string | 是 | 场景时间 | 剧本基本要素 |
| script.scenes[].characters_in_scene | array | 是 | 当前场景出场人物 | 支持场景卡片和拍摄理解 |
| script.scenes[].summary | string | 是 | 场景摘要 | 方便预览 |
| script.scenes[].conflicts | array | 是 | 场景冲突 | 体现戏剧推进 |
| script.scenes[].plot_points | array | 是 | 关键情节点 | 保留剧情结构 |
| script.scenes[].actions | array | 是 | 动作描写 | 将小说叙述转为可表演内容 |
| script.scenes[].actions[].actor | string | 是 | 动作执行者 | 明确人物行为 |
| script.scenes[].actions[].description | string | 是 | 动作内容 | 支持剧本初稿编辑 |
| script.scenes[].dialogues | array | 是 | 对白列表，可为空数组 | 支持对话少的小说 |
| script.scenes[].dialogues[].speaker | string | 是 | 说话人 | 剧本对白必需 |
| script.scenes[].dialogues[].line | string | 是 | 台词 | 剧本核心内容 |
| script.scenes[].dialogues[].emotion | string | 否 | 台词情绪 | 辅助表演和改写 |
| script.scenes[].narration | array | 是 | 旁白或场景说明 | 承接心理描写和环境描写 |
| script.scenes[].narration[].type | string | 是 | 旁白类型 | 区分 voice_over 和 scene_description |
| script.scenes[].narration[].text | string | 是 | 旁白文本 | 保留小说叙述信息 |
| script.scenes[].emotions | array | 是 | 情绪变化 | 体现人物心理转译 |
| script.scenes[].emotions[].character | string | 是 | 情绪所属人物 | 明确情绪主体 |
| script.scenes[].emotions[].emotion | string | 是 | 情绪描述 | 支持表演指导 |
| script.scenes[].emotions[].evidence | string | 是 | 原文依据或推断依据 | 防止 AI 随意编造 |
| script.scenes[].transitions | object | 是 | 转场信息 | 支持场景连续性 |
| script.scenes[].transitions.type | string | 是 | 转场类型 | 如 cut、fade_out |
| script.scenes[].transitions.next_scene_id | string | 否 | 下一场景 ID | 支持场景跳转 |
| script.scenes[].transitions.description | string | 否 | 转场说明 | 增强可读性 |
| script.scenes[].notes | array | 是 | 场景级改编说明 | 标注不确定和改写依据 |
| global_notes | array | 是 | 全局备注 | 说明整体改编策略 |

## 5. 为什么适合小说转剧本

小说文本通常包含章节、人物、叙述、心理、环境和对白。本 Schema 将这些内容映射为：

1. 人物信息进入 characters。
2. 原章节结构进入 chapters。
3. 剧本主体进入 script.scenes。
4. 心理描写转为 narration、emotions 或 notes。
5. 行为描写转为 actions。
6. 直接发言转为 dialogues。
7. 情节推进转为 plot_points 和 conflicts。

这样既保留小说来源，又形成剧本可编辑结构。

## 6. 可读性、可编辑性、可扩展性

可读性：

1. 字段名使用直观英文命名。
2. 顶层结构固定，评委和开发者能快速定位内容。
3. scene 是主要编辑单元，适合页面预览。

可编辑性：

1. YAML 可直接人工修改。
2. dialogues、actions、narration 均为数组，便于增删。
3. notes 字段可记录 AI 改编依据和不确定信息。

可扩展性：

1. metadata.version 支持版本演进。
2. genre 和 target_format 支持未来扩展到短剧、广播剧、有声书。
3. characters.aliases 支持人物别名归一。
4. 后续可在 scene 下增加 camera、props、sound、duration 等字段。

## 7. schemas/script.schema.yaml

```yaml
$schema: "https://json-schema.org/draft/2020-12/schema"
title: "Novel To Script YAML Schema"
type: object
additionalProperties: false
required:
  - metadata
  - source_info
  - characters
  - chapters
  - script
  - global_notes
properties:
  metadata:
    type: object
    additionalProperties: false
    required:
      - title
      - version
      - generated_at
      - language
      - target_format
    properties:
      title:
        type: string
        minLength: 1
      version:
        type: string
        minLength: 1
      generated_at:
        type: string
        minLength: 1
      language:
        type: string
        minLength: 1
      genre:
        type: string
      target_format:
        type: string
        minLength: 1
  source_info:
    type: object
    additionalProperties: false
    required:
      - source_type
      - chapter_count
    properties:
      source_type:
        type: string
        minLength: 1
      chapter_count:
        type: integer
        minimum: 3
      word_count:
        type: integer
        minimum: 0
      input_summary:
        type: string
  characters:
    type: array
    minItems: 1
    items:
      type: object
      additionalProperties: false
      required:
        - character_id
        - name
        - role
      properties:
        character_id:
          type: string
          minLength: 1
        name:
          type: string
          minLength: 1
        role:
          type: string
          minLength: 1
        description:
          type: string
        aliases:
          type: array
          items:
            type: string
        traits:
          type: array
          items:
            type: string
  chapters:
    type: array
    minItems: 3
    items:
      type: object
      additionalProperties: false
      required:
        - chapter_id
        - title
        - summary
      properties:
        chapter_id:
          type: string
          minLength: 1
        title:
          type: string
          minLength: 1
        summary:
          type: string
          minLength: 1
  script:
    type: object
    additionalProperties: false
    required:
      - scenes
    properties:
      scenes:
        type: array
        minItems: 1
        items:
          type: object
          additionalProperties: false
          required:
            - scene_id
            - source_chapter
            - location
            - time
            - characters_in_scene
            - summary
            - conflicts
            - plot_points
            - actions
            - dialogues
            - narration
            - emotions
            - transitions
            - notes
          properties:
            scene_id:
              type: string
              minLength: 1
            source_chapter:
              type: string
              minLength: 1
            location:
              type: string
              minLength: 1
            time:
              type: string
              minLength: 1
            characters_in_scene:
              type: array
              items:
                type: string
                minLength: 1
            summary:
              type: string
              minLength: 1
            conflicts:
              type: array
              items:
                type: string
            plot_points:
              type: array
              items:
                type: string
            actions:
              type: array
              items:
                type: object
                additionalProperties: false
                required:
                  - actor
                  - description
                properties:
                  actor:
                    type: string
                    minLength: 1
                  description:
                    type: string
                    minLength: 1
            dialogues:
              type: array
              items:
                type: object
                additionalProperties: false
                required:
                  - speaker
                  - line
                properties:
                  speaker:
                    type: string
                    minLength: 1
                  line:
                    type: string
                    minLength: 1
                  emotion:
                    type: string
            narration:
              type: array
              items:
                type: object
                additionalProperties: false
                required:
                  - type
                  - text
                properties:
                  type:
                    type: string
                    minLength: 1
                  text:
                    type: string
                    minLength: 1
            emotions:
              type: array
              items:
                type: object
                additionalProperties: false
                required:
                  - character
                  - emotion
                  - evidence
                properties:
                  character:
                    type: string
                    minLength: 1
                  emotion:
                    type: string
                    minLength: 1
                  evidence:
                    type: string
                    minLength: 1
            transitions:
              type: object
              additionalProperties: false
              required:
                - type
              properties:
                type:
                  type: string
                  minLength: 1
                next_scene_id:
                  type: string
                description:
                  type: string
            notes:
              type: array
              items:
                type: string
  global_notes:
    type: array
    items:
      type: string
```

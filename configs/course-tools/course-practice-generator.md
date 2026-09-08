# 章节练习题生成器

## 用途

`章节练习题生成器`（Tool ID：`course_practice_generator`）是一个 Open WebUI Workspace Tool。它**不使用固定题库**，不预置题目，也不保存历史题目；工具只校验输入并生成一次性的出题任务，课程 AI 助教再检索统一知识库 `course-knowledge-base`，按照约束临时出题。

## 输入参数

| 参数 | 类型 | 约束 |
|---|---|---|
| `course` | `string \| null` | 可选；只能是 `codex` 或 `math-modeling` |
| `chapter` | `string` | 必填；章节或知识模块，不能为空 |
| `difficulty` | `string` | `easy`、`medium`、`hard`，默认 `medium` |
| `count` | `integer` | 1–10，默认 3 |
| `question_types` | `list[string] \| null` | 可选，如概念题、简答题、代码题、建模题、综合题 |
| `student_level` | `string \| null` | 可选，如入门、基础、中级、进阶 |
| `include_answer` | `boolean` | 默认 `false`；是否给受控参考答案 |

非法参数返回 `status=error`、`error_code=INVALID_INPUT`、规范化约束和错误信息。合法参数返回 `status=ready`、`mode=temporary_generation` 和模型出题所需的约束及 JSON Schema。

## 出题与回答约束

- 出题前必须检索 `course-knowledge-base`，只能使用实际检索到且能支持题目的片段。
- 这是临时生成，不是确定性题库；若资料不足，输出“资料中未找到相关信息”，不强行补题。
- 不得编造文件名、章节、数据、引用或课程事实；每道题都标注真实资料来源。
- 实际可生成数量少于请求数量时，返回真实数量，不补造题目。
- 最终回答同时包含结构化 JSON 和 Markdown；每题有题型、题目、提示、知识点、`source.file` 和 `source.section`。
- `include_answer=false` 只输出题目、提示、知识点和来源；`true` 只能输出标明“参考答案”的思路、评分要点或简要答案，不代写可提交的整份作业或实验报告。

## Open WebUI 使用

1. 在工作区工具中同步或选择“章节练习题生成器”。
2. 在同一对话中确认课程 AI 助教已绑定 `course-knowledge-base`。
3. 直接指定章节、难度、数量和题型，例如：

```text
请根据 Codex CLI 章节，生成 3 道中等难度、适合基础水平学生的简答题，不要输出答案。
```

```text
请根据数学建模课程的 KMP 算法章节，生成 2 道简单代码题，并提供提示。
```

```text
请根据 Git/GitHub 工作流章节，生成 3 道进阶综合题，要求包含项目协作场景。
```

工具同步命令见根目录 `README.md` 和 `scripts/create_course_practice_generator_tool.py`；可先使用 `--dry-run` 检查源码，不会写入 Open WebUI。

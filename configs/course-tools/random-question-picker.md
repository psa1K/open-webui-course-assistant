# 随机抽题工具

## 用途

`随机抽题工具`（Tool ID：`random_question_picker`）是一个 Open WebUI Workspace Tool。它从**真实题库**（`data/question-bank.json`，23 题，题目依据 `knowledge/` 内真实课程资料编写，每题标注来源文件与章节）中按条件随机抽取题目。

与「章节练习题生成器」（临时生成）不同，本工具是**确定性题库随机抽样**：题目固定、来源可溯、可复现（支持 seed）。

## 输入参数

| 参数 | 类型 | 约束 |
|---|---|---|
| `course` | `string \| null` | 可选；`codex` 或 `math-modeling` |
| `chapter` | `string \| null` | 可选；模糊匹配题库章节关键词，如 `CLI`、`KMP` |
| `difficulty` | `string \| null` | 可选；`easy`、`medium`、`hard` |
| `question_type` | `string \| null` | 可选；`概念题`、`简答题`、`代码题`、`建模题`、`综合题` |
| `count` | `integer` | 1–10，默认 3 |
| `include_answer` | `boolean` | 默认 `false`；`true` 时选择题返回正确选项，简答/建模题返回参考要点 |
| `seed` | `integer \| null` | 可选；指定后抽取结果可复现（便于测试与复习定位） |

非法参数返回 `status=error`、`error_code=INVALID_INPUT` 与规范化约束；无匹配题目返回 `error_code=NO_MATCHING_QUESTIONS`。

## 输出结构

```json
{
  "status": "ok",
  "mode": "random_pick_from_bank",
  "bank_size": 23,
  "matched_pool_size": 4,
  "requested_count": 3,
  "picked_count": 3,
  "questions": [{
    "number": 1,
    "id": "CX-006",
    "course": "codex",
    "chapter": "Codex CLI 安装与上手",
    "difficulty": "easy",
    "type": "概念题",
    "question": "…",
    "options": ["…"],
    "hint": "…",
    "knowledge_points": ["…"],
    "source": {"file": "06-codex-cli-安装与上手.md", "section": "安装命令"}
  }],
  "notes": {"answer_policy": "默认不含答案；…"}
}
```

## 数据来源与维护

- 题库：`data/question-bank.json`（入库留档，题目与 `knowledge/` 资料一一对应）
- 安装器会把题库**内嵌**进工具源码（Workspace Tool 无文件系统访问），并校验：题量 ≥ 8、每题必含 `id/course/chapter/difficulty/type/question/source`、来源文件真实存在
- 扩充题库：修改 `data/question-bank.json` 后重新运行安装脚本即可

## Open WebUI 使用

```bash
# 安装/更新（题库内嵌 + 校验）
.venv/bin/python scripts/create_random_picker_tool.py --dry-run
.venv/bin/python scripts/create_random_picker_tool.py
```

对话中直接说：

```text
从 codex 课程的 CLI 章节随机抽 3 道中等难度的概念题，不要答案。
```

```text
随机抽 2 道数学建模的建模题，附参考答案，seed=42。
```

## 学术诚信

`include_answer=true` 仅提供自检用的参考答案/要点，不代写可提交的整份作业；工具不联网、不访问数据库、不含任何密钥。

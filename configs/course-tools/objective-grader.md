# 客观题自动判分工具

## 用途

`客观题自动判分工具`（Tool ID：`objective_grader`）是一个 Open WebUI Workspace Tool，对客观题（选择/多选/填空/判断）做**真实结构化判分**并输出解析，非提示词模拟。支持两种调用方式：

1. **基于题库判分** `grade_from_bank`：输入学生答题卡（JSON，键为题号），对照 `data/question-bank.json` 内嵌的真实标准答案判分。客观题（带 `options` + `answer_index` 的题）自动判分；简答/代码/建模/综合等主观题返回 `skipped=NOT_OBJECTIVE`，需人工判分。
2. **通用判分** `grade_answers`：调用方直接给题（可选类型 `choice` 单选 / `multi` 多选 / `text` 填空或判断），不依赖题库，用于临时/自定义客观题。

## 判分逻辑（真实结构化）

- **单选/概念题**：学生答案支持选项字母（`A`-`Z`）、1 起始序号（`1`/`第2个`）或选项文本（忽略大小写与空格、标点）——统一规整后与 `answer_index` 比较。
- **多选**：按字母/文本解析为选项下标集合，与标准答案集合做**无序相等**比较；支持列表或 `A,C`/`AC` 字符串。
- **填空/判断**：规范化（去空格、标点、转小写）后的**精确匹配**，标准答案可为多个可接受值（任一命中即对）。
- **计分**：每题默认 1 分，`points` 可加权；汇总 `total_points` / `earned_points` / `percentage`，可按 `pass_threshold`（默认 60）给出 `passed`。
- 无法识别/缺失字段的题不会崩溃：返回错误标注、记 0 分，或 `skipped` 跳过。

## 输入参数

| 参数 | 类型 | 约束 |
|---|---|---|
| `answer_sheet` | `string` | `grade_from_bank` 的答题卡 JSON，如 `{"CX-001":"B","MM-001":"2"}`，键为题号 |
| `items` | `string` | `grade_answers` 的题目 JSON 数组，每项含 `type/question/student_answer` 与正确值 |
| `pass_threshold` | `float` | 可选，默认 60（及格百分比） |
| `include_explanation` | `boolean` | 可选，默认 `true`；是否带解析字段 |

## 输出结构

```json
{
  "status": "ok",
  "mode": "objective_grading",
  "graded_count": 3,
  "correct_count": 2,
  "total_points": 3.0,
  "earned_points": 2.0,
  "percentage": 66.67,
  "passed": true,
  "skipped": [],
  "items": [{
    "id": "CX-001",
    "question": "…",
    "student_answer_normalized": "B",
    "standard_answer": "B Codex 能进入项目…",
    "correct": true,
    "points": 1.0,
    "earned_points": 1.0,
    "knowledge_points": ["…"],
    "source": {"file": "…", "section": "…"},
    "explanation": "…"
  }]
}
```

## 数据来源与维护

- 标准答案来自 `data/question-bank.json`（题库题目的 `options` + `answer_index`），来源与 `knowledge/` 资料一一对应。
- 安装器会校验题库完整性（题量 ≥ 8、必填字段、来源真实、工具含两个判分方法、无网络/数据库/敏感依赖）后内嵌题库。
- 扩充题库：修改 `data/question-bank.json` 后重新运行安装脚本即可。

## Open WebUI 使用

```bash
# 安装/更新（题库内嵌 + 校验）
.venv/bin/python scripts/create_objective_grader_tool.py --dry-run
.venv/bin/python scripts/create_objective_grader_tool.py
```

对话中直接说：

```text
用随机抽题工具抽 3 道概念题给我作答，然后用客观题判分工具按答题卡 {"CX-001":"B","CX-004":"C"} 判分。
```

```text
请判分以下填空：{"q1":{"type":"text","question":"KMP 前缀函数 pi[1]","correct":["0"],"student_answer":"0"}}
```

## 学术诚信

判分结果确定性、可解释（每题带标准答案与来源），仅用于自检与批改；主观题明确标注需人工判分，不代写作业。
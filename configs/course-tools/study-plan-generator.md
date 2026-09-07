# 学习计划生成工具

`学习计划生成工具`（Tool ID：`study_plan_generator`）根据 `data/course-catalog.json` 的结构化课程章节数据，校验用户目标、时间、课程和水平约束，并返回供课程 AI 助教生成计划的任务。它不是固定计划库：每次计划都根据输入临时生成。

## 输入

- `goal`：必填，课程学习目标；
- `duration`：必填，计划时长，`1–52` 的整数；
- `duration_unit`：`day` 或 `week`，默认 `week`；
- `course`：可选，`codex` 或 `math-modeling`；不填表示允许跨课程；
- `student_level`：可选，如入门、基础、中级、进阶；
- `hours_per_week`：每周可投入小时数，默认由调用方填写，必须大于 0 且不超过 168；
- `preferred_chapters`：可选，章节标题、编号或知识点关键词列表。

## 输出

校验通过返回 `status=ready`、`mode=study_plan_generation`、规范化 `plan_request`、目录匹配章节，以及直接可用的 `study_plan`。`study_plan` 已按用户时长分配真实章节到多个阶段，包含阶段目标、章节、学习活动、交付物、自测和真实资料来源。模型可据此补充面向学生的 Markdown 说明，但不得改写或虚构目录来源。

每个阶段至少包含：阶段编号、时间范围、目标、一个或多个真实目录章节、学习活动、阶段产出和自测方法。总阶段数应与计划时长一致或有明确合理的时间划分；必须结合学生水平与每周时长调整难度和任务量。

## 规则

- 只使用结构化课程目录中的真实章节、知识点和来源文件；
- 不得虚构章节、资料或完成时间；找不到指定章节时输出“资料中未找到相关信息”，不要强行生成；
- 计划是模型根据约束临时生成，不保存计划；
- 生成结果末尾提供“资料来源”，引用实际目录来源文件和章节；
- 如跨课程，分别标注课程来源；
- 工具只校验和组织约束，不联网、不读数据库、不保存密钥。

## 安装与调用

```bash
export OPENWEBUI_EMAIL="你的管理员邮箱"
export OPENWEBUI_PASSWORD="你的管理员密码"
.venv/bin/python scripts/create_study_plan_tool.py --base http://127.0.0.1:8080 --dry-run
.venv/bin/python scripts/create_study_plan_tool.py --base http://127.0.0.1:8080
```

在 Open WebUI 的“工作空间 → 工具”中选择 `学习计划生成工具`，示例请求：

> 我计划用 6 周、每周 5 小时学习 Codex，目标是掌握 CLI、MCP 和 Git/GitHub 工作流，当前水平为基础，请生成分阶段计划并标注资料来源。

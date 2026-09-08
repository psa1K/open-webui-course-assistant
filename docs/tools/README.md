# Workspace Tools 使用目录

本目录集中说明项目的 7 个 Open WebUI Workspace Tools。它们通过“工作空间 → 工具”安装，由用户在对话页选择启用。除随机抽题和客观题判分外，多数工具返回结构化约束或查询结果，再由课程 AI 助教结合统一知识库进行自然语言说明。

## 通用安装方式

在仓库根目录启动 Open WebUI 后，使用管理员账号执行对应脚本。所有脚本从环境变量读取凭据，不会把密码或 Token 写入仓库。

```bash
export OPENWEBUI_EMAIL="你的管理员邮箱"
export OPENWEBUI_PASSWORD="你的管理员密码"
```

先用每个脚本的 `--dry-run` 检查，再去掉该参数完成同步。同步成功后刷新 Open WebUI，在“工作空间 → 工具”确认工具存在；对话时还需在工具选择器中启用它。

## 工具总览

| 工具 | Tool ID | 主要用途 | 典型输入 | 详细说明 |
| --- | --- | --- | --- | --- |
| 章节练习题临时生成器 | `course_practice_generator` | 根据课程、章节、难度和数量生成临时出题任务 | 章节、难度、数量、题型、学生水平、是否给参考答案 | [说明](../../configs/course-tools/course-practice-generator.md) |
| 随机抽题工具 | `random_question_picker` | 从可追溯的固定题库按条件随机抽题 | 课程、章节、难度、题型、数量、随机种子 | [说明](../../configs/course-tools/random-question-picker.md) |
| 客观题自动判分工具 | `objective_grader` | 对选择、多选、填空、判断题做结构化评分与建议 | 题目、标准答案、学生答案或题库题目 ID | [说明](../../configs/course-tools/objective-grader.md) |
| 学习计划生成工具 | `study_plan_generator` | 按目标、时间和水平生成分阶段学习计划任务 | 目标、时长、课程、水平、每周时长、偏好章节 | [说明](../../configs/course-tools/study-plan-generator.md) |
| 课程章节查询工具 | `course_catalog_query` | 查询结构化课程章节、知识点和资料位置 | 关键词、课程、章节编号 | [说明](../../configs/course-tools/course-catalog-query.md) |
| 编程题测试用例生成工具 | `test_case_generator` | 生成真实可运行的编程题测试数据 | 内置模板或参考解、输入规格、数量、随机种子 | [说明](../../configs/course-tools/test-case-generator.md) |
| 知识点先修关系查询工具 | `knowledge_prerequisite_query` | 查询知识点的前置依赖、后续知识点和资料位置 | 知识点、是否包含间接关系 | [说明](../../configs/course-tools/knowledge-prerequisite-query.md) |

## 同步命令

```bash
# 章节练习题临时生成器
.venv/bin/python scripts/create_course_practice_generator_tool.py --base http://127.0.0.1:8080 --dry-run
.venv/bin/python scripts/create_course_practice_generator_tool.py --base http://127.0.0.1:8080

# 随机抽题工具
.venv/bin/python scripts/create_random_question_picker_tool.py --base http://127.0.0.1:8080 --dry-run
.venv/bin/python scripts/create_random_question_picker_tool.py --base http://127.0.0.1:8080

# 客观题自动判分工具
.venv/bin/python scripts/create_objective_grader_tool.py --base http://127.0.0.1:8080 --dry-run
.venv/bin/python scripts/create_objective_grader_tool.py --base http://127.0.0.1:8080

# 学习计划生成工具
.venv/bin/python scripts/create_study_plan_generator_tool.py --base http://127.0.0.1:8080 --dry-run
.venv/bin/python scripts/create_study_plan_generator_tool.py --base http://127.0.0.1:8080

# 课程章节查询工具
.venv/bin/python scripts/create_course_catalog_query_tool.py --base http://127.0.0.1:8080 --dry-run
.venv/bin/python scripts/create_course_catalog_query_tool.py --base http://127.0.0.1:8080

# 编程题测试用例生成工具
.venv/bin/python scripts/create_test_case_generator_tool.py --base http://127.0.0.1:8080 --dry-run
.venv/bin/python scripts/create_test_case_generator_tool.py --base http://127.0.0.1:8080

# 知识点先修关系查询工具
.venv/bin/python scripts/create_knowledge_prerequisite_query_tool.py --base http://127.0.0.1:8080 --dry-run
.venv/bin/python scripts/create_knowledge_prerequisite_query_tool.py --base http://127.0.0.1:8080
```

已存在同一 Tool ID 时，脚本会更新现有工具而不是重复创建。脚本报错时先确认 Open WebUI 正在运行、管理员账号正确，并检查模型或知识库是否已按 [用户指南](../user-guide/README.md) 配置。

## 选择工具的建议

| 你的目标 | 建议工具 | 示例 |
| --- | --- | --- |
| 根据指定章节临时练习 | `course_practice_generator` | “根据 Codex CLI 章节生成 2 道中等难度简答题，不要完整答案。” |
| 从已有题库抽题自测 | `random_question_picker` | “从 Codex 课程中随机抽 5 道基础题，seed=1。” |
| 批改客观题 | `objective_grader` | “按标准答案批改我的 5 道选择题，并指出薄弱知识点。” |
| 制定学习安排 | `study_plan_generator` | “我有 4 周、每周 6 小时，制定 Codex 入门学习计划。” |
| 查找章节与材料 | `course_catalog_query` | “查询 MCP 相关课程章节和资料位置。” |
| 为编程题造测试数据 | `test_case_generator` | “生成 5 组两数之和测试用例，seed=1。” |
| 查询学习依赖 | `knowledge_prerequisite_query` | “查询 MCP Server 的前置知识点和后续知识点。” |

## 共同边界

- 工具不得保存真实密码、Token、API Key 或本地数据库内容。
- 涉及课程事实时，来源应来自结构化数据或 `course-knowledge-base` 的实际检索结果；找不到资料时应说明“资料中未找到相关信息”。
- 章节练习题生成器默认不输出完整答案；即使显式要求参考答案，也只能给思路、评分要点或受控的简要参考，不能代写整份作业或实验报告。
- 工具输入不合法时应返回稳定的结构化错误，例如 `INVALID_INPUT`，而不是猜测用户意图或编造结果。

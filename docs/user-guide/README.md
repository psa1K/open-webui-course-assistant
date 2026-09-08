# 课程 AI 助教与知识库使用指南

本指南面向学生和项目部署者，说明如何在 Open WebUI 中使用课程 AI 助教、统一课程知识库和 Workspace Tools。工具的逐项参数与安装说明请看 [工具使用目录](../tools/README.md)。

## 使用前准备

完成根目录 [README](../../README.md) 的安装与启动步骤后，访问 <http://localhost:8080>。首次使用时需要：

1. 注册或登录 Open WebUI。
2. 在“设置 → 外部连接”配置可用的模型服务。
3. 使用管理员账号上传知识库、创建助教并同步需要的工具。

部署者可按下面顺序复现核心配置：

```bash
export OPENWEBUI_EMAIL="你的管理员邮箱"
export OPENWEBUI_PASSWORD="你的管理员密码"

.venv/bin/python scripts/upload_knowledge.py --base http://127.0.0.1:8080 --reset
.venv/bin/python scripts/create_course_assistant.py --base http://127.0.0.1:8080 --model deepseek-v4-flash
```

命令只从环境变量读取管理员凭据；不要把凭据写入文档、代码或 Git 提交。

## 课程 AI 助教

| 项目 | 默认值 |
| --- | --- |
| 名称 | 课程 AI 助教 |
| 助教 ID | `course-ai-assistant` |
| 模型 | `deepseek-v4-flash` |
| 知识库 | `course-knowledge-base` |
| 覆盖范围 | Codex 实战课程、数学建模课程及两者的跨课程问题 |

在新建对话时选择“课程 AI 助教”。助教会先判断问题属于 Codex、数学建模还是跨课程问题，并优先依据知识库中的实际资料回答。

助教支持：

- 课程知识问答与通俗解释；
- 按学生水平调整表达难度；
- 给出例题、示例代码、解题思路或分步检查方法；
- 根据指定章节生成练习题；
- 分析学生答案并给出改进建议；
- 给出实际检索资料的文件名与章节/片段；
- 对课程外问题、资料缺失问题和虚构引用请求作出明确提示。

完整助教规则见 [系统提示词](../../configs/course-assistant/system-prompt.md) 与 [助教配置](../../configs/course-assistant/assistant.json)。

## 回答、引用与学术诚信

正常回答按“结论 → 解释/步骤 → 资料依据 → 注意事项”组织。引用必须来自实际检索结果，格式如下：

```text
资料来源：
- 文件：06-codex-cli-安装与上手.md
- 章节/片段：相关检索片段
```

助教不会把知识库名称当作资料文件，也不会编造文件、章节、数据或引用。若当前知识库没有可支撑回答的资料，应明确说明：**“资料中未找到相关信息。”**

对作业、实验、报告或编程任务，助教优先给提示、思路、步骤、评分要点和检查方法，不直接代写整份可提交成果。生成的例题、示例代码或参考思路属于助教临时生成内容，不是课程资料原文。

## 常见提问方式

```text
Codex 有哪些使用入口？请用适合入门学生的方式解释，并给出资料来源。
```

```text
根据 Codex CLI 章节生成 3 道中等难度、适合基础学生的简答题，不要完整答案。
```

```text
我每周能学习 6 小时，计划 4 周完成 Codex 基础学习。请生成分阶段学习计划。
```

```text
查询 MCP Server 的前置知识点和后续知识点，并告诉我对应课程资料位置。
```

## 使用 Workspace Tools

在对话页打开工具选择器，勾选需要的工具，再以自然语言给出参数。工具的作用是校验约束、查询结构化资料或生成结构化任务；需要知识库事实或自然语言解释时，仍应让课程 AI 助教结合 `course-knowledge-base` 回答。

所有工具的 Tool ID、同步命令、示例输入、输出格式和限制都在 [工具使用目录](../tools/README.md)。工具没有显示时，请由管理员按照该目录中的安装命令同步，再刷新 Open WebUI 页面。

## 验收与问题排查

统一知识库的六类真实 RAG 验收记录位于 [docs/rag/verification-results.json](../rag/verification-results.json)。系统层面的两轮 15 项测试、优化批准记录和前后对比位于 [系统测试与评价归档](../system-evaluation/README.md)。

如果回答未引用资料、来源无关或工具无法调用：

1. 确认当前对话选择的是“课程 AI 助教”。
2. 确认 `course-knowledge-base` 已上传且存在。
3. 确认模型服务可用。
4. 确认所需 Workspace Tool 已同步并在当前对话中启用。
5. 根据根 README 的 RAG 验证命令复测，不要把无关检索片段当作有效资料。

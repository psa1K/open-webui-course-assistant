# open-webui-course-assistant

「软件工程编程实训」课程项目 *课程专属 AI 助手*（李正丹、朱静雯 出题）。

基于 [Open WebUI](https://github.com/open-webui/open-webui) 开发课程专属 AI 助手，利用其模型配置、系统提示词、知识库（RAG）和工具扩展能力，帮助学生学习、复习与自测。

## 团队成员

- **psa1K** (Jialiang Cai)
- **eco-NIN** (Yuzhe Guo)

## 当前进度

- [x] 系统部署：Open WebUI 已在本机通过 pip/uv 方式部署并启动（[#14](https://github.com/psa1K/open-webui-course-assistant/issues/14)）
- [x] 模型接入：已连接 DeepSeek API（deepseek-v4-flash / deepseek-v4-pro / deepseek-v4-flash-vision-exp），管理员账号已创建
- [x] 课程知识库搭建（[#15](https://github.com/psa1K/open-webui-course-assistant/issues/15)）：`codex-course`（16 个文件）+ `math-modeling`（2 个文件），RAG 检索已验证
- [x] 统一课程知识库 RAG 检索与引用（[#16](https://github.com/psa1K/open-webui-course-assistant/issues/16)）：18 个资料文件已上传到一个 `course-knowledge-base`；2026-09-04 使用 `deepseek-v4-flash` 完成 6 类真实最终回答验收，检索引用、无答案处理与防编造检查均通过
- [x] 课程 AI 助教（[#17](https://github.com/psa1K/open-webui-course-assistant/issues/17)）：已创建并绑定 `course-knowledge-base`，系统提示词和 8 项课程助教能力检查完成
- [x] 章节练习题临时生成器（[#18](https://github.com/psa1K/open-webui-course-assistant/issues/18)）：已同步 `course_practice_generator`，并完成本机 Open WebUI 实际对话验收
- [x] 随机抽题工具（[#19](https://github.com/psa1K/open-webui-course-assistant/issues/19)）：真实题库（23 题，来源 knowledge/ 资料）+ `random_question_picker` 已安装，function calling 验证通过
- [x] 客观题自动判分工具（[#20](https://github.com/psa1K/open-webui-course-assistant/issues/20)）：`objective_grader` 真实结构化判分（选择/多选/填空/判断），题库对照或通用两种模式，已安装并验证
- [ ] 学习计划生成工具（[#21](https://github.com/psa1K/open-webui-course-assistant/issues/21)）：`study_plan_generator` 根据结构化课程目录和用户目标/时间/水平约束生成分阶段计划；离线验证已通过，待本机 Open WebUI 实际同步与调用验收
- [x] 课程章节查询工具（[#22](https://github.com/psa1K/open-webui-course-assistant/issues/22)）：结构化课程目录（22 章）+ `course_catalog_query` 关键词/章节查询，已安装并验证
- [x] 编程题测试用例生成工具（[#23](https://github.com/psa1K/open-webui-course-assistant/issues/23)）：7 个内置模板 + 自定义参考解，受限命名空间运行参考解生成真实可运行用例，已安装并验证
- [ ] 系统测试与评价（[#25](https://github.com/psa1K/open-webui-course-assistant/issues/25)）
- [ ] 成果提交（[#26](https://github.com/psa1K/open-webui-course-assistant/issues/26)）

## 安装与部署

### 克隆并复现（推荐）

本项目设计为可复现：全新 clone 后按以下步骤即可在任意机器上跑通（依赖版本由 `requirements.lock` 锁定）：

```bash
# 1. 克隆仓库
git clone git@github.com:psa1K/open-webui-course-assistant.git
cd open-webui-course-assistant

# 2. 配置自己的密钥（复制模板并填入你自己的 DeepSeek API key）
cp .env.example .env
#   编辑 .env，把 OPENAI_API_KEY 改为你自己的 key（Open WebUI 会自动加载 .env）

# 3. 一键安装（创建 Python 3.11 虚拟环境 + 按锁文件安装依赖）
./scripts/setup.sh

# 4. 启动
.venv/bin/open-webui serve
```

启动后访问 http://localhost:8080，注册管理员账号即可使用。

### 手动安装（等价步骤）

```bash
# 创建虚拟环境
uv venv --python 3.11 .venv

# 按锁文件安装依赖（保证版本一致）
uv pip install --python .venv/bin/python -r requirements.lock

# 启动服务
.venv/bin/open-webui serve
```

> 官方也支持 Docker 部署，参见 [Open WebUI README](https://github.com/open-webui/open-webui#how-to-install-)。

### 连接大语言模型

在 Open WebUI 的 **设置 → 外部连接 → OpenAI API** 中添加模型服务（如本地 Ollama 或 OpenAI 兼容 API），保存后即可在对话中选择模型。也可通过管理员 API 配置：

```bash
# 需先用管理员账号登录获取 token，然后：
curl -X POST http://localhost:8080/openai/config/update \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"ENABLE_OPENAI_API":true,
       "OPENAI_API_BASE_URLS":["https://api.deepseek.com"],
       "OPENAI_API_KEYS":["<DEEPSEEK_API_KEY>"],
       "OPENAI_API_CONFIGS":{}}'
```

本仓库已接入 DeepSeek API（OpenAI 兼容，base_url `https://api.deepseek.com`），可用模型：`deepseek-v4-flash`、`deepseek-v4-pro`、`deepseek-v4-flash-vision-exp`。

## 使用说明

1. 首次访问 http://localhost:8080，注册管理员账号
2. 在设置中配置模型连接
3. 在「工作空间」中创建课程专属模型/智能体（系统提示词 + 知识库 + 工具）
4. 在知识库中上传课程资料，启用 RAG

### 上传统一课程知识库

确保本地 Open WebUI 已启动，并在 `.env` 或当前终端设置管理员凭据：

```bash
export OPENWEBUI_EMAIL="你的管理员邮箱"
export OPENWEBUI_PASSWORD="你的管理员密码"
# 若本机环境设置了代理，推荐使用 127.0.0.1 避免 localhost 请求被代理转发
.venv/bin/python scripts/upload_knowledge.py --base http://127.0.0.1:8080 --reset
```

脚本会将 `knowledge/` 下 Codex 实战课程和数学建模资料全部上传到同一个 `course-knowledge-base` 知识库。若服务不在默认地址，可使用 `--base http://localhost:8080`。上传完成后运行最终回答验收（脚本会自动发现模型，也可显式指定）：

```bash
.venv/bin/python scripts/verify_rag.py --base http://127.0.0.1:8080
# 或：
.venv/bin/python scripts/verify_rag.py --base http://127.0.0.1:8080 --model "模型名称"
```

脚本会在同一个 `course-knowledge-base` 上执行 6 类测试：直接问答、章节定位、跨资料综合、知识库无答案、错误引用防护、引用格式检查。结果写入 `docs/rag/verification-results.json`；输出文件只保留脱敏的命中片段摘要和验收字段，不保存密码、token、API Key 或本地数据库。

## 课程 AI 助教（Issue #17）

课程助教配置位于 `configs/course-assistant/`，默认名称为“课程 AI 助教”，使用 `deepseek-v4-flash`，绑定唯一统一知识库 `course-knowledge-base`，覆盖 Codex 实战课程和数学建模课程。配置不包含密码、Token 或 API Key。

先检查配置（不会创建或更新 Open WebUI 模型）：

```bash
export OPENWEBUI_EMAIL="你的管理员邮箱"
export OPENWEBUI_PASSWORD="你的管理员密码"
.venv/bin/python scripts/create_course_assistant.py --base http://127.0.0.1:8080 --model deepseek-v4-flash --dry-run
```

确认无误后创建或同步工作空间模型；若同 ID 模型已存在，脚本会更新它：

```bash
.venv/bin/python scripts/create_course_assistant.py --base http://127.0.0.1:8080 --model deepseek-v4-flash
```

可用 `--knowledge-id` 指定已确认的 Knowledge ID，`--name` 覆盖助教名称，`--model` 覆盖底层模型。脚本会检查模型和 Knowledge 是否存在，并使用 `trust_env=False` 避免本地代理影响请求。Issue #17 已完成：助教已在本机 Open WebUI 创建并绑定统一 Knowledge，系统提示词已覆盖 8 项课程助教能力及学术诚信要求；配置检查记录保存在 `docs/assistant/verification-results.json`。

## 章节练习题临时生成器（Issue #18）

Issue #18 采用临时出题，不使用确定性题库或预置题目。Workspace Tool `章节练习题生成器`（Tool ID：`course_practice_generator`）只负责校验课程、章节、难度、数量、题型、学生水平和答案开关，并返回结构化出题任务；课程 AI 助教再结合统一知识库 `course-knowledge-base` 的实际检索片段生成题目。工具源码和详细约束见 `tools/course_practice_generator.py` 与 `configs/course-tools/course-practice-generator.md`。

先做不写入 Open WebUI 的源码检查：

```bash
.venv/bin/python scripts/create_course_tool.py --base http://127.0.0.1:8080 --dry-run
```

设置本机管理员凭据后同步工具（已存在时更新，不重复创建）：

```bash
export OPENWEBUI_EMAIL="你的管理员邮箱"
export OPENWEBUI_PASSWORD="你的管理员密码"
.venv/bin/python scripts/create_course_tool.py --base http://127.0.0.1:8080
```

可用 `--tool-id` 和 `--name` 覆盖默认值。工具支持 `course`、`chapter`、`difficulty`、`count`、`question_types`、`student_level`、`include_answer`；输出必须同时包含结构化 JSON 和 Markdown。默认不输出完整答案，显式开启 `include_answer` 时也只提供受控的参考思路、评分要点或简要答案。

Issue #18 已完成：工具已同步到本机 Open WebUI，并完成 Codex CLI、Git/GitHub、数学建模、学生水平、答案开关、无资料拒答、虚构引用防护和结构化输出等实际对话验收。脱敏结果位于 `docs/tools/verification-results.json`，交互过程位于 `interactions/eco-NIN/interactions.md`。

## 目录结构

```
├── AGENTS.md              # 团队协作约定（交互记录、PR-merge、README 维护、可复现性）
├── README.md              # 本文件
├── .env.example           # 环境变量模板（真实密钥放本机 .env，不入库）
├── requirements.lock      # 依赖锁定（uv pip freeze，保证环境一致）
├── scripts/
│   ├── setup.sh           # 一键安装脚本
│   ├── export_units.py    # 把课程 HTML 拆分为单元 Markdown
│   └── upload_knowledge.py# 上传 knowledge/ 到 Open WebUI 知识库
├── interactions/          # 成员与 AI Agent 的交互记录
│   ├── README.md          # 记录约定说明
│   ├── psa1K/
│   └── eco-NIN/
├── tools/                 # Open WebUI Workspace Tools
│   ├── course_practice_generator.py
│   ├── random_question_picker.py
│   ├── objective_grader.py
│   ├── course_catalog_query.py
│   └── test_case_generator.py
├── data/
│   ├── question-bank.json # 随机抽题题库（23 题，来源 knowledge/ 资料）
│   └── course-catalog.json# 结构化课程目录（22 章，章节/知识点/资料位置）
├── configs/course-tools/  # 工具用途、参数和输出规范
├── docs/tools/            # 工具验收记录
├── knowledge/             # 课程知识库原始资料
│   ├── README.md          # 资料索引
│   ├── codex-course/      # Codex 实战课程（14 单元 MD + PDF + 示例代码）
│   └── math-modeling/     # 数学建模课程（Lecture1.pdf + tex）
└── .venv/                 # 虚拟环境（不入库）
```

## 克隆后验证清单

- [ ] `./scripts/setup.sh` 成功安装（.env 已存在）
- [ ] `.venv/bin/open-webui serve` 启动，`curl http://localhost:8080/api/health` 返回正常
- [ ] 管理员账号可登录，模型列表可见 DeepSeek 模型

## 测试与优化记录

- Issue #16 配置：`configs/course-knowledge-base/`
- Issue #16 测试模板：`tests/rag-test-template.md`
- Issue #16 脱敏验收结果：`docs/rag/verification-results.json`
- Issue #17 助教配置：`configs/course-assistant/`
- Issue #17 验收记录：`docs/assistant/verification-results.json`
- Issue #18 工具配置：`configs/course-tools/course-practice-generator.md`
- Issue #18 验收记录：`docs/tools/verification-results.json`
- Issue #19 工具配置：`configs/course-tools/random-question-picker.md`
- Issue #19 题库：`data/question-bank.json`；离线测试：`tests/test_random_picker_tool.py`
- Issue #20 工具配置：`configs/course-tools/objective-grader.md`
- Issue #20 测试：`tests/test_objective_grader_tool.py`
- Issue #21 工具配置：`configs/course-tools/study-plan-generator.md`；源码：`tools/study_plan_generator.py`；安装脚本：`scripts/create_study_plan_tool.py`；离线测试：`tests/test_study_plan_tool.py`
- Issue #22 工具配置：`configs/course-tools/course-catalog-query.md`
- Issue #22 目录：`data/course-catalog.json`；离线测试：`tests/test_course_catalog_tool.py`
- Issue #23 工具配置：`configs/course-tools/test-case-generator.md`
- Issue #23 测试：`tests/test_test_case_generator_tool.py`


## 学习计划生成工具（Issue #21）

`学习计划生成工具`（Tool ID：`study_plan_generator`）接受学习目标、计划时长、课程、学生水平、每周学习时长和偏好章节，基于 `data/course-catalog.json` 的结构化章节数据返回分阶段计划生成任务。工具不保存固定计划，也不调用网络或数据库；Open WebUI 中的课程 AI 助教依据真实目录生成 JSON + Markdown 计划，并标注章节来源。

```bash
export OPENWEBUI_EMAIL="你的管理员邮箱"
export OPENWEBUI_PASSWORD="你的管理员密码"
.venv/bin/python scripts/create_study_plan_tool.py --base http://127.0.0.1:8080 --dry-run
.venv/bin/python scripts/create_study_plan_tool.py --base http://127.0.0.1:8080
```

同步成功后，在 Open WebUI 的“工作空间 → 工具”中选择“学习计划生成工具”。配置说明和调用示例见 `configs/course-tools/study-plan-generator.md`。

Issue #16 已于 2026-09-04 通过 6 类真实最终回答测试：直接问答、章节定位、跨资料综合、知识库无答案、错误引用防护和引用格式检查。验证使用 `deepseek-v4-flash`，结果保存在 `docs/rag/verification-results.json`。后续资料或模型配置变化后，应重新运行验收；不能仅凭上传成功或检索接口返回片段宣称通过。

## 相关链接

- 题目：`2. 李正丹-朱静雯老师的题目.docx`
- Open WebUI 官方文档：https://docs.openwebui.com/

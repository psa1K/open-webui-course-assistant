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
- [ ] 课程 AI 助教（[#17](https://github.com/psa1K/open-webui-course-assistant/issues/17)）：配置已归档，待本机创建与 8 类功能验收
- [ ] 自定义扩展功能（[#18](https://github.com/psa1K/open-webui-course-assistant/issues/18) 等）
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

可用 `--knowledge-id` 指定已确认的 Knowledge ID，`--name` 覆盖助教名称，`--model` 覆盖底层模型。脚本会检查模型和 Knowledge 是否存在，并使用 `trust_env=False` 避免本地代理影响请求。Issue #17 只有在实际创建成功并完成 8 类功能验收后才标记为完成；结果保存在 `docs/assistant/verification-results.json`。

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

Issue #16 已于 2026-09-04 通过 6 类真实最终回答测试：直接问答、章节定位、跨资料综合、知识库无答案、错误引用防护和引用格式检查。验证使用 `deepseek-v4-flash`，结果保存在 `docs/rag/verification-results.json`。后续资料或模型配置变化后，应重新运行验收；不能仅凭上传成功或检索接口返回片段宣称通过。

## 相关链接

- 题目：`2. 李正丹-朱静雯老师的题目.docx`
- Open WebUI 官方文档：https://docs.openwebui.com/

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
- [ ] RAG 检索与引用（[#16](https://github.com/psa1K/open-webui-course-assistant/issues/16)）
- [ ] 课程 AI 助教（[#17](https://github.com/psa1K/open-webui-course-assistant/issues/17)）
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

见各功能 issue 的验收标准；测试结果与优化前后对比将归档到 `docs/` 或对应 issue。

## 相关链接

- 题目：`2. 李正丹-朱静雯老师的题目.docx`
- Open WebUI 官方文档：https://docs.openwebui.com/

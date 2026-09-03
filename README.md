# open-webui-course-assistant

「软件工程编程实训」课程项目 *课程专属 AI 助手*（李正丹、朱静雯 出题）。

基于 [Open WebUI](https://github.com/open-webui/open-webui) 开发课程专属 AI 助手，利用其模型配置、系统提示词、知识库（RAG）和工具扩展能力，帮助学生学习、复习与自测。

## 团队成员

- **psa1K** (Jialiang Cai)
- **eco-NIN** (Yuzhe Guo)

## 当前进度

- [x] 系统部署：Open WebUI 已在本机通过 pip/uv 方式部署并启动（[#14](https://github.com/psa1K/open-webui-course-assistant/issues/14)）
- [ ] 课程知识库搭建（[#15](https://github.com/psa1K/open-webui-course-assistant/issues/15)）
- [ ] RAG 检索与引用（[#16](https://github.com/psa1K/open-webui-course-assistant/issues/16)）
- [ ] 课程 AI 助教（[#17](https://github.com/psa1K/open-webui-course-assistant/issues/17)）
- [ ] 自定义扩展功能（[#18](https://github.com/psa1K/open-webui-course-assistant/issues/18) 等）
- [ ] 系统测试与评价（[#25](https://github.com/psa1K/open-webui-course-assistant/issues/25)）
- [ ] 成果提交（[#26](https://github.com/psa1K/open-webui-course-assistant/issues/26)）

## 安装与部署

### 前置条件

- Python 3.11（建议使用 [uv](https://docs.astral.sh/uv/) 管理虚拟环境）
- 至少一种大语言模型的访问方式（本地 Ollama 或 OpenAI 兼容 API）

### 安装 Open WebUI

```bash
# 创建虚拟环境
uv venv --python 3.11 .venv

# 安装 Open WebUI
uv pip install --python .venv/bin/python open-webui

# 启动服务
.venv/bin/open-webui serve
```

启动后访问 http://localhost:8080。

> 官方也支持 Docker 部署，参见 [Open WebUI README](https://github.com/open-webui/open-webui#how-to-install-)。

### 连接大语言模型

在 Open WebUI 的 **设置 → 外部连接 → OpenAI API** 中添加模型服务（如本地 Ollama 或 OpenAI 兼容 API），保存后即可在对话中选择模型。

## 使用说明

1. 首次访问 http://localhost:8080，注册管理员账号
2. 在设置中配置模型连接
3. 在「工作空间」中创建课程专属模型/智能体（系统提示词 + 知识库 + 工具）
4. 在知识库中上传课程资料，启用 RAG

## 目录结构

```
├── AGENTS.md              # 团队协作约定（交互记录、PR-merge、README 维护）
├── README.md              # 本文件
├── interactions/          # 成员与 AI Agent 的交互记录
│   ├── psa1K/
│   └── eco-NIN/
├── knowledge/             # 课程知识库原始资料（按章节分类）
└── .venv/                 # 虚拟环境（不入库）
```

## 测试与优化记录

见各功能 issue 的验收标准；测试结果与优化前后对比将归档到 `docs/` 或对应 issue。

## 相关链接

- 题目：`2. 李正丹-朱静雯老师的题目.docx`
- Open WebUI 官方文档：https://docs.openwebui.com/

# 核心功能：自动化、插件与 Skill

> unit: unit-automation-plugin-skill | type: source

## 一句话结论

自动化让 Codex 按计划跑任务，插件扩展能力，Skill 让 Codex 复用工作方法——三者组合能让 Codex 真正成为工程搭档。

## 第三篇：核心功能详解

### 自动化

#### 什么是自动化

**Codex 自动化 = 让 Codex 不只是“听你指挥”，而是能按规则定期帮你巡查项目、发现问题、处理问题。**

就像你给项目请了一个“AI 值班工程师”：

> 平时它不打扰你， 有问题它来提醒你， 简单问题它先尝试修， 最后让你审核决定。

#### 如何使用自动化

可以用“每周 Codex 会话自动复盘”举例，让 Codex 越来越好用。

你可以让 Codex 定期检查最近一段时间的会话记录、任务结果和常见问题，沉淀成一份可复用的工作流档案。

示例提示词可以这样写：

```
请检索并复盘最近一周的 Codex 会话记录与执行日志，维护一份“Codex 会话复盘与个人风格档案”。

要求：
1. 优先使用可用的会话历史检索能力；如果需要读取日志，只做搜索、元数据提取和相关片段抽取，不要整文件载入大型 session 文件。
2. 不要复现原始日志、隐私内容、密钥、内部 reasoning 或长对话原文。
3. 总结执行经验：哪些做法导致了问题，最终正确做法是什么，适合什么场景复用。
4. 总结我的偏好：UI 设计偏好、产品理念、交互原则、内容系统偏好和工作流偏好。
5. 整理可复用规则清单：把复盘结论改写成后续 Codex 会话可以遵循的简洁规则。
6. 更新文档时去重、合并相近规则，保留日期范围或任务类型作为来源线索。
7. 如有适合长期复用的规则，请建议是否加入项目级或用户级 AGENTS.md。
```

![Codex平台的自动化页面](assets/source/0f83f244267dd6.png)

![Codex桌面端界面，左侧为功能导航栏，其中“自动化”选项被选中](assets/source/706a9745820ae3.png)

### 插件

给 Codex 额外安装的“能力包”

#### 什么是插件

Codex 本身已经能读代码、改代码、运行命令；插件是在这个基础上，让它连接更多工具、使用固定流程，或者获得某些专项能力。

#### 插件、Skill、MCP 三者关系（先看这一张表）

插件、Skill、MCP 是本篇最容易混淆的三个概念。它们不是互相替代，而是各管一层，下面这张总表请先记住，后面各节不再重复对比。

对比 插件 Plugin Skill MCP

一句话 能力安装包 一套固定工作方法 连接外部工具的接口 解决什么问题 安装、打包、分发能力 同类任务「怎么做」 「连接什么工具或数据」 范围 最大，可打包 Skill、MCP 等 较小，单类任务的流程 单个外部工具或数据源的连接 类比 工具箱 工具箱里的说明书 给工具箱接电的插座 谁来用 普通用户也能一键安装 普通用户也能用 更偏开发者和团队配置 举例 GitHub 插件、Figma 插件 README Skill、代码 Review Skill 数据库 MCP、文档 MCP

一句话记住：**插件可以把 Skill 和 MCP 打包成更容易安装的能力包；Skill 管「怎么做」，MCP 管「连什么工具」。**

#### 在 Codex 桌面端里怎么安装插件

##### 打开 Codex 桌面端

![Codex App中插件页面](assets/source/47dc564d28b7d2.png)

##### 搜索或浏览插件

也可以搜索对应的插件

![Codex App中插件页面](assets/source/23e248ba7d3bee.png)

##### 点开插件详情

![Codex App中GitHub插件的详情页面](assets/source/87c8267ef051f9.png)

##### 点击 Add to Codex 或添加按钮

![在Codex App中插件详情页面的界面](assets/source/6eac016005149c.png)

##### 安装完成后，新开一个 thread 使用

![Codex App中“hello - Codex”项目页面](assets/source/b78c5578449d9b.png)

#### 在 Codex CLI 里怎么安装插件

进入项目目录后，先启动 Codex：

```
codex
```

然后在 Codex CLI 里输入：

```
/plugins
```

打开插件列表后，可以：

操作 说明

搜索插件 找你需要的插件 查看详情 看插件能做什么、需要什么权限 Install plugin 安装插件 Uninstall plugin 卸载插件 Space 对已安装插件启用或停用

#### 常见插件和能力方向

插件目录会随着 Codex 版本、工作区和账号权限变化。下面不是固定排名，而是常见能力方向，实际可安装内容以你当前 Codex 插件页显示为准。

类型 包含插件 适合做什么

浏览器与电脑操作 Chrome、Computer Use 网页测试、自动点击、软件操作 代码与项目协作 GitHub 管理仓库、修 bug、创建 PR 前端与设计 Build Web Apps、Figma 生成网页、设计稿转代码 办公交付 Documents、Presentations、Spreadsheets 文档、PPT、表格分析 视频生成 HyperFrames、Remotion 用代码或 HTML 生成视频

序号 插件 / 能力 主要作用 简单来说

1 Chrome 让 Codex 直接操作浏览器 可以打开网页、点击按钮、检查页面效果、测试网页功能 2 GitHub 代码仓库管理与协作 让 Codex 读取仓库、处理 issue、改代码、创建 PR 3 Computer Use 让 Codex 操作电脑 像人一样看屏幕、点按钮、操作软件，权限比较高 4 Build Web Apps 一句话生成前端网页应用 输入需求，生成网页、小工具、落地页、Demo 5 Figma 设计稿转代码与原型设计 把 Figma 设计稿变成前端页面，适合 UI 开发 6 Documents AI 帮你交付正式文档 生成 README、项目说明、教程文档、产品文档 7 Presentations AI 生成高质量 PPT 根据内容生成汇报、课程、产品介绍、方案型 PPT 8 Spreadsheets AI 数据分析与表格处理 帮你整理 Excel、分析数据、生成表格结论 9 HyperFrames HTML 直接生成视频 用网页/HTML 结构生成视频内容 10 Remotion 用代码生成高质量视频 用 React/代码方式生成更专业的视频

### Skill

给 Codex 准备的一套「固定工作方法」。

Codex 本身会读代码、改代码、运行命令。

但如果你经常让它做同一类任务，比如写 README、做代码 Review、生成网页、整理文档，就可以把这套流程做成 Skill。

#### 用 README Skill 看懂它怎样工作

用户给出一次任务，Codex 匹配可复用的 Skill，并按照 Skill 内部定义的步骤完成交付。

01 · 本次输入

##### Prompt

“请分析当前项目，并生成一份适合新手阅读的 README。”

02 · 可复用方法

##### README Skill

**Skill 内部工作流：**读取项目 → 确认命令 → 组织内容 → 检查准确性。

03 · 本次输出

##### README.md

生成项目介绍、安装步骤、启动命令和目录说明。

> **关键区别：**Prompt 是这一次的具体要求；Skill 是可重复使用的方法包；Workflow 和 Instruction 都属于 Skill 内部的执行规则。

#### README Skill 的目录结构

最小可用的 Skill 只需要 `SKILL.md`；其余目录按实际任务需要添加。

```
.agents/
└── skills/
    └── readme-skill/
        ├── SKILL.md          # 必需：触发条件、工作流程和输出要求
        ├── references/       # 可选：README 规范或项目术语
        ├── scripts/          # 可选：收集项目结构、校验命令
        ├── assets/           # 可选：README 模板或示例资源
        └── agents/
            └── openai.yaml  # 可选：界面信息和工具依赖
```

组成 是否必需 在 README Skill 中的作用

`SKILL.md` 必需 定义触发条件、执行流程和长期规则。 `references/` 可选 保存规范、领域知识、数据结构和详细资料。 `scripts/` 可选 把重复且要求稳定的操作变成可执行脚本。 `assets/` 可选 保存模板、图片、字体和示例文件等交付资源。 `agents/openai.yaml` 可选 提供展示名称、说明和默认提示词等界面信息。

`SKILL.md`

`references/`

`scripts/`

`assets/`

`agents/openai.yaml`

**记住：** 用户用 Prompt 说明“这次要什么”，Skill 负责规定“每次都怎么做”。

记住：

用户用 Prompt 说明“这次要什么”，Skill 负责规定“每次都怎么做”。

---

#### Skill 还是 MCP？什么时候用哪个

插件、Skill、MCP 的整体区别，见前面「插件、Skill、MCP 三者关系」总表。这里只解决最常见的纠结：一个需求到底该用 Skill 还是 MCP。

记住一句话：**「怎么做」的问题用 Skill，「连接什么工具」的问题用 MCP。**

你的需求 用 Skill 还是 MCP

写 README、固定文档输出格式 Skill 做代码 Review、UI Review Skill 生成落地页、把修 bug 流程标准化 Skill 查最新开发文档、新版本 API MCP 连接数据库 MCP 读取 Figma 设计稿 MCP 读取 GitHub issue / PR MCP 连接 Notion、内部知识库、公司内部工具 MCP

#### Skill 和普通提示词有什么区别

只做一次的任务 = 直接写提示词 经常重复做的任务 = 适合做 Skill

对比维度 普通提示词 Skill

使用方式 每次手动输入 保存成固定能力 稳定性 容易漏要求 更稳定 适合场景 临时任务 重复任务 复用性 低 高 内容结构 一段提示词 指令、模板、资料、脚本 适合谁 所有人 经常重复做同类任务的人

#### Skill 适合什么时候用

情况 是否适合做 Skill

同一类任务经常重复做 适合 每次都要写一堆规则 适合 想让 Codex 输出更稳定 适合 团队里多人要用同一套流程 适合 一次性小任务 不一定需要 临时改一句文案 不需要 只是问一个概念 不需要

#### Skill 的基本结构

一个简单 Skill 可以这样写：

```
# Skill 名称

## 适用场景
这个 Skill 适合用来做什么。

## 工作目标
Codex 最终要交付什么结果。

## 工作流程
1. 先分析输入内容
2. 再确认任务类型
3. 然后按固定步骤处理
4. 最后输出结果和检查清单

## 输出格式
规定 Codex 最后应该怎么输出。

## 注意事项
哪些事情不能做，哪些风险要提醒。
```

比如 README Skill：

```
# README 生成 Skill

## 适用场景
用于根据当前项目生成 README 文档。

## 工作目标
输出一份结构清晰、适合新手阅读的 README。

## 工作流程
1. 阅读项目结构
2. 查看 package.json 或主要入口文件
3. 判断项目类型
4. 生成项目介绍
5. 补充安装步骤和启动命令
6. 说明文件结构
7. 输出常见问题

## 输出格式
使用 Markdown 格式。

## 注意事项
不要编造不存在的功能。
不确定的地方要明确标注。
```

#### 在 Codex 桌面端里怎么添加 Skill

在 Codex 桌面端里添加 Skill，可以分成两种情况：

```
1. 使用已有 Skill
2. 创建自己的 Skill
```

##### 使用已有 Skill

在插件里面的技能可以看到系统推荐的一些Skill

![Codex App中技能相关界面](assets/source/524e81164e1c08.png)

##### 创建自己的 Skill

如果你想自己创建一个 Skill，可以在 Codex 桌面端的 thread 里使用：

```
$skill-creator
```

它相当于一个 Skill 创建助手，会帮你把一套重复流程整理成 Skill。

操作步骤：

步骤 操作

1 打开 Codex 桌面端 2 选择一个项目 3 新建一个 thread 4 输入 `$skill-creator` 5 告诉它你想创建什么 Skill 6 提供使用场景、规则、示例输出 7 让 Codex 生成 Skill 文件 8 检查生成结果 9 之后在新 thread 里使用这个 Skill

`$skill-creator`

示例提示词：

```
$skill-creator

请帮我创建一个 README Skill。

这个 Skill 的作用：
根据当前项目自动生成适合小白阅读的 README。

触发场景：
当我说“生成 README”“写项目说明”“整理项目文档”时使用。

工作流程：
1. 先阅读项目结构
2. 查看 package.json、README、入口文件
3. 判断项目类型
4. 生成项目简介
5. 写安装步骤
6. 写启动命令
7. 说明主要文件夹作用
8. 补充常见问题
9. 不确定的地方不要编造

输出格式：
使用 Markdown。

必须包含：
- 项目简介
- 功能特点
- 安装步骤
- 启动命令
- 文件结构
- 常见问题
- 后续优化方向
```

##### 推荐安装的 Skill

Skill / 项目 主要作用 GitHub 地址

Superpowers 给 Coding Agent 加一整套“软件开发方法论”：先澄清需求、写规格、做实现计划，再按 TDD / 任务拆分推进开发。适合 Codex、Claude Code、Cursor、Gemini CLI 等工程型 Agent。 [https://github.com/obra/superpowers](https://github.com/obra/superpowers) skill-creator 创建 Skill 的辅助 Skill。Codex 内置或可用的 Skill 以你当前环境显示为准；不同来源的同名 Skill 可能实现不同。 以当前 Codex Skill 列表为准 baoyu-skills 宝玉整理的一组实用 Skills，偏内容创作和日常效率：小红书图文、文章配图、漫画、公众号发布、X/微博发布、网页转 Markdown、YouTube 字幕、AI 生图等。仓库说明里写的是给 Claude Code、Codex 等 AI Agents 提效用，并建议按需安装。 [https://github.com/JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills) Agent Reach 给 Agent 装“联网能力”：读网页、YouTube、RSS、GitHub、Twitter/X、B站、Reddit、小红书、LinkedIn 等，还带诊断和多后端路由。简单说就是让本地 Agent 能更方便地搜网、读平台内容。 [https://github.com/Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach) find-skills “找 Skill 的 Skill”。当你问“有没有某某功能的 Skill”时，它会帮你搜索、发现、安装 Agent Skills；底层配合 npx skills find / add / check / update 使用。 [https://github.com/vercel-labs/skills/tree/main/skills/find-skills](https://github.com/vercel-labs/skills/tree/main/skills/find-skills)

https://github.com/obra/superpowers

https://github.com/JimLiu/baoyu-skills

https://github.com/Panniantong/Agent-Reach

https://github.com/vercel-labs/skills/tree/main/skills/find-skills

#### 在 Codex CLI 里怎么添加 Skill

在 Codex CLI 里添加 Skill，主要有 3 种方式：

```
1. 使用已有 Skill
2. 用 $skill-creator 创建 Skill
3. 手动创建 SKILL.md 文件
```

##### 添加 Skill 的 3 种方式

方式 适合谁 简单来说 推荐程度

使用已有 Skill 刚入门用户 直接调用现成技能 推荐 `$skill-creator` 创建 想把提示词变成 Skill 的人 让 Codex 帮你整理 Skill 最推荐 手动创建 `SKILL.md` 熟悉文件结构的人 自己写 Skill 文件 进阶

`$skill-creator`

`SKILL.md`

---

###### 方式一：使用已有 Skill

进入项目目录后，先启动 Codex CLI：

```
cd 项目目录
codex
```

进入 Codex CLI 后，可以输入：

```
/skills
```

或者直接输入：

```
$
```

Codex 会显示当前可用的 Skill。

如果你已经知道 Skill 名称，也可以直接在任务里点名使用：

```
请使用 $readme-skill，根据当前项目生成 README。
```

或者：

```
$ui-review-skill 请检查当前首页的视觉问题，并给出修改建议。
```

---

###### 已有 Skill 的使用方式

用法 示例 适合场景

/skills 打开 Skill 列表 不知道有哪些 Skill 时 输入 $ 快速选择 Skill 想快速调用时 `$skill-name` `$readme-skill` 明确知道 Skill 名称时 自然语言描述 请用 README Skill 写项目说明 不确定具体名称时

`$skill-name`

`$readme-skill`

---

###### 方式二：用 `$skill-creator` 创建 Skill

如果你想把一套重复流程保存成 Skill，可以用：

```
$skill-creator
```

它相当于一个 Skill 创建助手，会问你：

问题 目的

这个 Skill 是做什么的 明确用途 什么时候触发 写清楚适用场景 要不要包含脚本 判断是否只是指令型 Skill 输出格式是什么 保证结果稳定 有哪些限制 避免乱改、乱编、乱执行

---

###### `$skill-creator` 使用流程

步骤 操作 目的

1 进入项目目录 确保 Skill 生成在正确项目里 2 运行 `codex` 打开 Codex CLI 3 输入 `$skill-creator` 启动 Skill 创建助手 4 描述 Skill 用途 告诉它要做什么 5 补充触发场景 告诉它什么时候用 6 补充工作流程 固定 Codex 的执行步骤 7 补充输出格式 保证结果稳定 8 检查生成结果 确认 `SKILL.md` 是否合理 9 重新打开或继续使用 测试 Skill 是否生效

`codex`

`$skill-creator`

`SKILL.md`

---

###### `$skill-creator` 示例提示词

```
$skill-creator

请帮我创建一个 README Skill。

这个 Skill 的作用：
根据当前项目自动生成一份适合小白阅读的 README。

触发场景：
当我说“生成 README”“写项目说明”“整理项目文档”“写安装教程”时使用。

工作流程：
1. 先阅读项目结构
2. 查看 package.json、README、入口文件
3. 判断项目类型
4. 生成项目简介
5. 写安装步骤
6. 写启动命令
7. 说明主要文件夹作用
8. 补充常见问题
9. 不确定的地方不要编造

输出格式：
使用 Markdown。

必须包含：
- 项目简介
- 功能特点
- 安装步骤
- 启动命令
- 文件结构
- 常见问题
- 后续优化方向

注意事项：
不要编造不存在的功能。
不要读取或输出 API Key、密码、token、私钥。
```

---

###### 方式三：手动创建 Skill 文件

Skill 本质上是一个文件夹，里面必须有一个：

```
SKILL.md
```

最简单的结构是：

```
.agents
└── skills
    └── readme-skill
        └── SKILL.md
```

也可以放脚本、参考资料和资源文件：

```
.agents
└── skills
    └── readme-skill
        ├── SKILL.md
        ├── scripts
        ├── references
        └── assets
```

---

###### Skill 文件结构说明

文件 / 文件夹 是否必须 作用

`SKILL.md` 必须 写 Skill 的名称、描述和具体指令 scripts/ 可选 放可执行脚本 references/ 可选 放参考文档、标准、说明 assets/ 可选 放模板、图片、资源文件

`SKILL.md`

---

###### 一个最简单的 `SKILL.md` 示例

```
---
name: readme-skill
description: 当用户需要生成 README、项目说明、安装教程、启动步骤时使用。
---

你是一个 README 文档生成助手。

任务：
根据当前项目生成一份适合新手阅读的 README。

工作流程：
1. 阅读项目结构
2. 查看 package.json、README、入口文件
3. 判断项目类型
4. 生成项目介绍
5. 写安装步骤
6. 写启动命令
7. 说明文件结构
8. 补充常见问题
9. 不确定的地方不要编造

输出格式：
使用 Markdown。

必须包含：
- 项目简介
- 功能特点
- 安装步骤
- 启动命令
- 文件结构
- 常见问题
- 后续优化方向
```

#### 添加 Skill 后怎么使用

添加 Skill 后，有两种常见用法：

用法 示例

明确指定 Skill 请使用 `$readme-skill` 生成 README 让 Codex 自动判断 帮我写一份项目 README

`$readme-skill`

如果 Skill 的 description 写得清楚，Codex 会更容易自动判断什么时候该用它。

比如：

```
description: 当用户需要生成 README、项目说明、安装教程、启动步骤时使用。
```

这个描述就很清楚。

不建议写得太模糊：

```
description: 帮我写东西。
```

这样 Codex 不知道什么时候该调用它。

#### Skill 的四种作用域

Skill 的保存位置决定了它能在哪些范围内使用。一般来说，项目专属流程放在项目级，跨项目复用的个人方法放在个人级；需要统一分发时，再考虑管理员级或系统级。

作用域 保存位置 使用范围

项目级 `REPO` 项目中的 `.agents/skills/` 只在当前项目及对应子目录使用 个人级 `USER` 个人 Skills 目录 你的所有项目都可以使用 管理员级 `ADMIN` 机器或组织统一目录 该机器或组织中的用户可用 系统级 `SYSTEM` Codex 内置 所有用户可用，例如 Skill Creator

`REPO`

`.agents/skills/`

`USER`

`ADMIN`

`SYSTEM`

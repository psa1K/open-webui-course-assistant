# 核心功能：MCP 与 Git / GitHub 工作流

> unit: unit-mcp-git | type: source

## 一句话结论

MCP 让 Codex 接入外部工具，Git 工作流让 Codex 的改动可追踪、可回滚、可审查——这是工程化使用 Codex 的基础。

### MCP(Model Context Protocol)

**只有进阶AI编程才需要了解，普通人可以直接跳过**

让 Codex 连接外部工具的接口。

Codex 本身可以读代码、改代码、运行命令。

MCP 的作用是让 Codex 连接更多外部工具、数据源或服务。

#### 什么是 MCP

概念 简单来说

MCP 连接外部工具的标准接口 MCP Server 提供工具能力的服务 Tool Codex 可以调用的具体功能 Config MCP 的配置文件 STDIO Server 通过本地命令启动的 MCP 服务 HTTP Server 通过网址连接的 MCP 服务 Context 外部工具提供给 Codex 的上下文信息

MCP 就像 AI 世界的 USB 接口标准，MCP Server 是接入的设备，Tool 是设备提供的具体功能。生活化理解：

```
Codex = 一个会干活的人
MCP = 给他接上不同工具的插座
MCP Server = 插在插座上的工具箱
Tool = 工具箱里的具体工具
```

比如一个文档 MCP，可以让 Codex 读取文档。

一个数据库 MCP，可以让 Codex 查询数据库。

一个设计工具 MCP，可以让 Codex 获取设计稿信息。

---

#### MCP 适合做什么

场景 MCP 可以怎么用

查开发文档 连接文档 MCP，让 Codex 查新版本 API 连接数据库 让 Codex 查询数据库结构或测试数据 连接设计工具 让 Codex 读取设计稿、组件信息 连接项目管理工具 读取 issue、任务、需求说明 连接内部系统 调用公司内部工具或数据源 连接知识库 让 Codex 根据团队文档工作 连接自动化工具 让 Codex 调用额外脚本或服务

```
普通写代码，不一定需要 MCP。
需要 Codex 访问外部工具或外部数据时，才考虑 MCP。
```

#### MCP Server 是什么

MCP Server 可以理解成：

给 Codex 提供工具能力的服务。

比如：

MCP Server 类型 能提供什么

文档 MCP 查询开发文档、API 文档 数据库 MCP 查询表结构、读取测试数据 GitHub MCP 读取 issue、PR、仓库信息 Figma MCP 读取设计稿信息 Notion MCP 读取知识库页面 浏览器 MCP 访问网页、获取页面信息 内部工具 MCP 连接公司自己的系统

简单来说：

```
MCP Server = Codex 可以调用的外部工具服务。
```

#### 在 Codex 桌面端里怎么使用 MCP

##### Codex 桌面端使用 MCP 的基本流程

步骤 操作 简单来说

1 打开 Codex 桌面端 进入桌面版 Codex 2 进入 Settings 打开设置 3 找到 MCP servers 进入 MCP 工具管理区 4 查看 recommended servers 查看官方或系统推荐的 MCP 5 添加 custom server 添加自己的 MCP server 6 按提示完成授权 有些 MCP 需要登录外部账号 7 回到项目 thread 在任务里调用 MCP 8 查看结果和权限请求 确认 Codex 调用了什么工具

![Codex App中MCP Server的设置界面](assets/source/1a791d5ae88ebc.png)

##### 添加 MCP 时通常需要填什么

配置项 作用 简单来说

Name MCP 名称 给这个工具起名字 Command / URL 启动命令或服务地址 Codex 通过它连接工具 Type MCP 类型 本地命令型或远程 HTTP 型 Env 环境变量 放 token、配置项等 Auth 授权方式 是否需要登录外部账号 Enabled tools 启用哪些工具 只打开需要的功能

![Codex App中添加MCP时的设置界面](assets/source/d55755a3d4277d.png)

##### 添加 MCP 后怎么使用

添加完成后，回到 Codex 桌面端的 thread，直接描述任务即可。

用法 示例

直接描述需求 请查一下 Next.js App Router 的最新用法 明确要求使用 MCP 请使用可用的 MCP 工具查询这个库的文档 指定某个 MCP 请用 context7 查询 Next.js 的最新文档 先查看可用工具 当前有哪些 MCP 工具可以用？

示例提示词：

```
请使用可用的 MCP 文档工具，
查询 Next.js App Router 的最新用法，
然后告诉我当前项目应该怎么修改。
```

或者：

```
请用 Figma MCP 读取这个设计稿，
分析页面结构，并给我生成前端实现计划。
```

#### 在 Codex CLI 里怎么使用 MCP

在 Codex CLI 里使用 MCP，可以理解成：

给终端版 Codex 接入外部工具。

比如：

```
文档 MCP：让 Codex 查询开发文档
GitHub MCP：让 Codex 读取 issue、PR、仓库信息
Figma MCP：让 Codex 读取设计稿
数据库 MCP：让 Codex 查询数据库结构
```

```
Codex CLI = 终端里的 AI 编程助手
MCP = 给 Codex CLI 接外部工具的接口
```

---

##### CLI 使用 MCP 的基本流程

步骤 操作 简单来说

1 打开终端 PowerShell / Terminal 2 进入项目目录 让 Codex 知道当前项目 3 添加 MCP server 给 Codex 接入外部工具 4 检查 MCP 是否添加成功 确认工具已经可用 5 启动 Codex CLI 进入 Codex 对话界面 6 用 /mcp 查看工具 看当前能用哪些 MCP 7 在任务里调用 MCP 让 Codex 使用外部工具 8 查看结果和权限提示 确认是否安全

---

##### 常用 MCP 终端命令

命令 作用 简单来说

`codex mcp --help` 查看 MCP 命令帮助 不知道怎么用时先看 `codex mcp list` 查看已配置 MCP server 看现在接了哪些外部工具 `codex mcp add` 添加 MCP server 给 Codex 增加一个外部工具 `codex mcp remove` 删除 MCP server 不用了就移除 `codex mcp get` 查看某个 MCP server 详情 看具体配置 `codex mcp login` 登录需要授权的 MCP 给某些远程 MCP 授权 `codex mcp logout` 退出某个 MCP 授权 取消连接状态 /mcp 在 Codex 会话里查看 MCP 看当前会话能调用哪些工具

`codex mcp --help`

`codex mcp list`

`codex mcp add`

`codex mcp remove`

`codex mcp get`

`codex mcp login`

`codex mcp logout`

---

##### 添加 MCP 的基本格式

添加 MCP 的基本命令通常是：

```
codex mcp add 名称 -- 启动命令
```

简单来说：

```
名称 = 你给这个 MCP 起的名字
启动命令 = 这个 MCP 怎么启动
```

示例：

```
codex mcp add context7 -- npx -y @upstash/context7-mcp
```

这条命令可以理解成：

```
给 Codex 添加一个叫 context7 的 MCP。
它通过 npx 启动 @upstash/context7-mcp 这个工具。
```

---

##### 查看已经添加的 MCP

添加后可以运行：

```
codex mcp list
```

作用：

```
查看当前 Codex CLI 已经配置了哪些 MCP server。
```

如果能看到你刚添加的名称，说明配置已经写入。

---

##### 进入 Codex 后查看 MCP

先进入项目目录：

```
cd 项目目录
```

然后启动 Codex：

```
codex
```

进入 Codex CLI 后，输入：

```
/mcp
```

作用：

```
查看当前会话里可用的 MCP 工具。
```

如果 MCP 没显示，可能是：

问题 可能原因

没添加成功 `codex mcp add` 命令失败 MCP 启动失败 依赖没装或命令错误 名称写错 调用时写错 server 名 需要授权 还没登录外部服务 配置没刷新 需要重启 Codex CLI

`codex mcp add`

---

##### 在任务里调用 MCP

配置好 MCP 后，不一定要记复杂命令。

你可以直接在 Codex CLI 里说：

```
请使用可用的 MCP 工具，查询 Next.js App Router 的最新文档。
```

也可以指定某个 MCP：

```
请用 context7 查询 Next.js App Router 的最新用法，
然后告诉我当前项目应该怎么修改。
```

如果是 Figma 类 MCP，可以这样说：

```
请用 Figma MCP 读取这个设计稿，
分析页面结构，并给我生成前端实现计划。
```

如果是 GitHub 类 MCP，可以这样说：

```
请用 GitHub MCP 查看这个仓库最近的 open issue，
帮我整理出优先级最高的 3 个问题。
```

---

##### MCP 配置文件在哪里

Codex 的 MCP 配置会写进配置文件里。

常见位置是：

```
~/.codex/config.toml
```

简单来说：

```
config.toml = Codex 的配置文件
```

里面可能会有类似这样的配置：

```
[mcp_servers.context7]
command = "npx"
args = ["-y", "@upstash/context7-mcp"]
```

这表示：

```
有一个 MCP server 叫 context7。
启动命令是 npx -y @upstash/context7-mcp。
```

如果你不熟悉配置文件，前期不要手动乱改。

优先使用：

```
codex mcp add
codex mcp list
codex mcp remove
```

---

##### 添加远程 MCP

有些 MCP 不是本地命令启动，而是通过网址连接。

这类一般叫远程 MCP / HTTP MCP。

可能会需要：

配置项 简单来说

URL 远程 MCP 服务地址 Auth 是否需要登录 Token 访问凭证 OAuth 浏览器授权登录

如果需要登录，可以使用：

```
codex mcp login MCP名称
```

不用了可以：

```
codex mcp logout MCP名称
```

初学建议：

```
先用不需要复杂授权的文档类 MCP。
后面再尝试需要登录的远程 MCP。
```

---

##### 删除不用的 MCP

如果某个 MCP 不用了，可以删除：

```
codex mcp remove 名称
```

比如：

```
codex mcp remove context7
```

删除后再检查：

```
codex mcp list
```

确认它已经不在列表里。

[MCP Python SDK 官方文档 ↗](https://py.sdk.modelcontextprotocol.io/)

### 代码管理 （Git 与 GitHub 工作流）

用 Codex 做真实项目时，要掌握 Git 和 GitHub。

```
Git = 本地代码版本管理工具
GitHub = 把代码放到网上协作的平台
Codex = 帮你读代码、改代码、跑命令的 AI 编程助手
```

一句话：

```
Git 负责记录代码变化。
GitHub 负责远程保存和协作。
Codex 负责帮你完成具体编程任务。
```

#### Git 和 GitHub 有什么区别

对比 Git GitHub

简单来说 本地版本管理工具 代码云盘 + 协作平台 主要作用 记录代码每次改了什么 远程保存代码、团队协作 使用位置 你的电脑里 浏览器 / 云端 核心能力 commit、branch、diff、merge repository、issue、pull request 是否必须联网 不需要 需要 和 Codex 的关系 Codex 改完代码后，用 Git 检查和保存 Codex Web / Cloud 常和 GitHub 配合

##### Git 概念

概念 简单来说 作用

Repository 一个代码仓库 存放整个项目 Commit 一次代码存档 记录这次改了什么 Branch 分支 在不影响主线的情况下改代码 Diff 改动对比 看新增、删除、修改了什么 Stage 暂存区 准备把哪些改动保存进 commit Merge 合并 把一个分支的改动合到另一个分支 Conflict 冲突 两边改了同一处代码，需要手动选择 Push 推送 把本地代码上传到 GitHub Pull 拉取 把 GitHub 上的新代码同步到本地 Clone 克隆 从 GitHub 下载一个项目到本地

---

##### GitHub 概念

概念 简单来说 作用

Repository GitHub 上的项目仓库 存代码 Issue 问题 / 需求记录 记录 bug、需求、任务 Pull Request / PR 代码合并申请 改完代码后申请合并 Main Branch 主分支 项目的稳定版本 Feature Branch 功能分支 用来开发新功能 Review 代码检查 合并前检查代码 Actions 自动化流程 自动测试、构建、部署 README 项目说明书 告诉别人项目怎么用 .gitignore 忽略文件清单 防止上传无关或敏感文件

---

#### 为什么用 Codex 更需要 Git

场景 为什么需要 Git

Codex 改了很多代码 可以查看具体改了哪里 Codex 改错了 可以回退到之前版本 Codex 删除了不该删的内容 可以用 Git 找回 多次让 Codex 修改 每次 commit 保存一个阶段 想让 Codex 大胆试方案 用 branch 或 worktree 隔离风险 要把项目放到 GitHub 需要 push 到远程仓库 团队协作 需要 PR、review、merge

一句话：

```
没有 Git，Codex 改错了你很难回退。
有了 Git，Codex 可以放心试，你可以随时检查和恢复。
```

---

#### 如何在 Codex 中使用 Git

步骤 操作 目的

1 初始化 Git 让项目开始被 Git 管理 2 写好 .gitignore 防止上传垃圾文件和密钥 3 先 commit 一次 保存干净版本 4 新建分支 给 Codex 一个安全实验区 5 让 Codex 修改代码 完成具体任务 6 查看 diff 检查 Codex 改了什么 7 运行项目 / 构建 确认没出错 8 满意后 commit 保存这次修改 9 push 到 GitHub 上传远程仓库 10 创建 PR 合并前再检查一次

##### 在 Codex 对话框中输入：把项目初始化成一个 Git 工程，并排除不需要的文件

![在Codex中使用Git的界面](assets/source/47a225e702eaf1.png)

---

##### Codex 会帮我们直接写好 .gitignore 文件

![在Codex中使用Git的界面](assets/source/6d5d940627fd9b.png)

#### 如何在 Codex 中使用 GitHub

##### 使用前需要准备什么

准备项 作用 简单来说

GitHub 账号 保存远程代码 代码云盘账号 Git 本地版本管理 记录代码变化 GitHub 仓库 放项目代码 一个远程项目文件夹 本地项目 Codex 要修改的代码 电脑里的项目文件夹 GitHub 登录权限 允许 push / PR 证明这是你的仓库 .gitignore 防止上传无关文件 不上传垃圾文件和密钥

##### 标准上传流程

步骤 操作 目的

1 在 GitHub 新建仓库 创建一个远程项目空间 2 复制仓库地址 后面要连接本地项目 3 将地址复制给 Codex 让 Codex 知道要上传到哪个仓库 4 推送到 GitHub 正式上传代码

###### 创建 GitHub 仓库

![GitHub创建仓库页面](assets/source/d4a0131b39cf7c.png)

###### 复制仓库地址

![在GitHub上创建仓库时复制仓库地址的操作界面](assets/source/7d12b72d58d527.png)

###### 将地址复制给 Codex

![Codex平台中“做一个首页”项目的页面](assets/source/0fce51b9e92f49.png)

###### 推送到 GitHub

#### 代码回滚

##### 修改代码

先让 AI 修改一下代码

![Codex平台中“做一个首页”项目的界面](assets/source/200b91673d4271.png)

##### 提交到 Git，保存好当前版本

![Codex平台中使用Git进行代码管理的操作界面](assets/source/616ab0545d020d.png)

##### 继续修改代码

![在Codex中使用Git的代码回滚操作界面](assets/source/eb280f46b93df5.png)

##### 打开 IDE 查看代码并且回退代码

先打开 IDE 查看代码

![在Codex中使用Git的界面](assets/source/7acf3c1961b9ac.png)

##### 复制版本号

![在VS Code中使用Codex进行代码回滚的操作界面](assets/source/3edadb260488b1.png)

##### 复制给 Codex，让它回退代码到指定版本

![在Codex中使用Git进行代码回滚的操作界面](assets/source/c8f189968ee7fa.png)

#### Git Worktree

给同一个 Git 项目，额外开一个独立工作副本。

相当于一个草稿本，效果满意后再合并回正式项目。

##### 为什么需要 Worktree

普通 Git 分支虽然可以切换，但每次只能在一个文件夹里操作一个分支。

Worktree 的好处是：

场景 Worktree 的作用

想让 Codex 大胆改代码 给它单独开一个副本 不想影响当前项目 主项目保持不动 想同时做多个任务 每个任务一个 worktree 想比较多个方案 方案 A / B / C 分开放 改坏了不想要 直接丢掉 worktree 做大改动 / 重构 降低污染主项目的风险

##### 创建 Worktree

![Codex移动版界面中“hello - Codex”项目的操作菜单](assets/source/328d98ab4aa414.png)

![Codex平台界面，左侧为项目列表，其中“hello - codex_2”项目被红色框突出显示](assets/source/1ae514a3837c24.png)

##### 使用分支进行任务

![Gitpod界面中“hello - codex_2”分支的代码编辑区域](assets/source/3fe11c8e695b42.png)

##### 合并回主干

检查效果满意后，就可以合并回主干，并把这个分支删除。

![在GitHub上使用Worktree进行代码管理的操作界面](assets/source/af4ac25b193d92.png)

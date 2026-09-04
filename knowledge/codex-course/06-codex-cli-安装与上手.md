# Codex CLI 安装与上手

> unit: unit-cli-install | type: source

## 一句话结论

Codex CLI 是贴近工程实际的入口，npm/brew/Windows 都能装，支持 ChatGPT 登录和 API Key 登录，终端命令和斜杠命令要分清楚。

### Codex CLI 安装与上手

Codex CLI 是 Codex 的命令行版本。

它适合愿意打开终端的人使用，比如 PowerShell、Terminal、iTerm、Windows Terminal。

#### macOS / Linux 安装

macOS 有两种常见安装方式。

##### 方式一：使用 npm 安装

先确认电脑已经安装 Node.js。

打开 Terminal，输入：

```
node -v
npm -v
```

能看到版本号，说明 Node.js 和 npm 已经可用。

然后安装 Codex CLI：

```
npm install -g @openai/codex@latest
```

安装完成后，检查是否安装成功：

```
codex --version
```

或者直接运行：

```
codex
```

---

##### 方式二：使用 Homebrew 安装

Mac 用户也可以用 Homebrew：

```
brew install --cask codex
```

安装后运行：

```
codex
```

初学建议：

- 已经装过 Node.js，就用 npm。

- 已经习惯 Homebrew，就用 brew。

#### Windows 安装

Windows 用户建议使用 PowerShell 或 Windows Terminal。

第一步，安装 Node.js。

安装完成后，打开 PowerShell，输入：

```
node -v
npm -v
```

能看到版本号，说明安装成功。

第二步，安装 Codex CLI：

```
npm install -g @openai/codex@latest
```

第三步，检查是否安装成功：

```
codex --version
```

或者直接运行：

```
codex
```

Windows 用户第一次使用时，建议不要在系统目录里运行 Codex。

不要在这些位置直接操作：

```
C:\
系统目录
桌面
下载文件夹
重要资料文件夹
```

建议新建一个练习目录：

```
D:\AI-Codex-Projects\hello-codex
```

#### 第一次运行

安装完成后，在终端输入：

```
codex
```

第一次运行时，Codex 会提示你登录。

Codex CLI 常见有两种登录方式：

```
1. 使用 ChatGPT 账号登录
2. 使用 OpenAI API Key 登录
```

新手优先推荐第一种：ChatGPT 账号登录。

##### 方式一：使用 ChatGPT 账号登录

这是最适合普通用户和小白的方式。

在终端输入：

```
codex
```

或者：

```
codex login
```

然后选择：

```
Sign in with ChatGPT
```

登录流程大概是：

```
1. 终端输入 codex 或 codex login
2. 选择 Sign in with ChatGPT
3. 浏览器会自动打开登录页面
4. 输入你的 ChatGPT 账号
5. 登录成功后，浏览器会把登录结果传回终端
6. 回到终端，Codex CLI 就可以使用了
```

##### 方式二：使用 API Key 登录

Codex CLI 也支持使用 OpenAI API Key 登录。

API Key 登录更适合开发者、自动化脚本、CI/CD、服务器任务等场景。

```
ChatGPT 登录 = 走 ChatGPT 账号和套餐额度
API Key 登录 = 走 OpenAI Platform API 计费
```

如果你要用 API Key 登录，先去 OpenAI Platform 创建 API Key。

然后在终端里设置环境变量。

macOS / Linux 可以这样写：

```
export OPENAI_API_KEY="你的_API_Key"
printenv OPENAI_API_KEY | codex login --with-api-key
```

Windows PowerShell 可以这样写：

```
$env:OPENAI_API_KEY="你的_API_Key"
$env:OPENAI_API_KEY | codex login --with-api-key
```

登录成功后，Codex CLI 会保存登录信息，后面再次运行：

```
codex
```

就可以继续使用。

---

##### ChatGPT 登录和 API Key 登录有什么区别？

对比 ChatGPT 账号登录 API Key 登录

适合人群 普通用户、小白 开发者、自动化、CI/CD 使用额度 跟 ChatGPT 套餐有关 按 OpenAI Platform API 计费 上手难度 更简单 稍复杂 是否推荐小白 推荐 不推荐一开始用 适合本地练习 适合 也可以，但没必要 适合自动化脚本 一般 更适合

##### API Key 登录注意事项

API Key 很敏感，不能随便泄露。

不要把 API Key：

```
写进代码里
发给别人
截图公开
上传到 GitHub
放进 README
放进前端网页
提交到 Git 仓库
```

如果不小心泄露了 API Key，要立刻去 OpenAI Platform 删除或重新生成。

API Key 登录虽然方便做自动化，但它会按 API 使用量计费，所以新手不要不清楚费用规则就长时间运行任务。

---

##### 查看当前登录状态

你可以用下面命令查看当前是否已经登录：

```
codex login status
```

如果需要退出登录，可以运行：

```
codex logout
```

退出后，下次再运行 Codex CLI，需要重新登录。

#### CLI 基础命令

Codex CLI 的命令可以分成两类：

类型 使用位置 作用

终端命令 PowerShell / Terminal 里输入 启动、登录、更新、诊断、管理 Codex 斜杠命令 进入 Codex 后输入 切模型、调权限、看 diff、生成规则、退出会话

##### CLI 终端命令

CLI 终端命令，是在 PowerShell / Terminal / Windows Terminal 里输入的命令。

###### 小白最常用终端命令

命令 作用 简单来说 使用场景

`codex` 启动 Codex CLI 打开终端版 Codex 进入项目后使用 `codex --version` 查看版本 检查是否安装成功 安装后第一步 `codex --help` 查看帮助 查看支持哪些命令 不知道命令怎么用时 `codex login` 登录 Codex 用 ChatGPT 账号或 API Key 登录 第一次使用 `codex login status` 查看登录状态 看当前有没有登录 登录异常时 `codex logout` 退出登录 清除本机登录状态 换账号、公共电脑 `codex doctor` 检查环境问题 自动生成诊断报告 启动失败、登录失败、环境异常 `codex update` 更新 Codex 更新 CLI 版本 需要升级时 `codex app` 打开 Codex 桌面端 从终端打开桌面版 想切到图形界面时

`codex`

`codex --version`

`codex --help`

`codex login`

`codex login status`

`codex logout`

`codex doctor`

`codex update`

`codex app`

---

###### 进入项目相关命令

命令 作用 示例 简单来说

`cd 项目目录` 进入项目文件夹 `cd D:\\AI-Codex-Projects\\hello-Codex` 先走到项目里面 `codex` 在当前目录启动 Codex `codex` 让 Codex 在当前项目工作 `codex --cd 项目路径` 指定目录启动 `codex --cd D:\\AI-Codex-Projects\\hello-Codex` 不用先 cd，直接指定项目 `codex -C 项目路径` —cd 的简写 `codex -C ./hello-Codex` 更短写法

`cd 项目目录`

`cd D:\\AI-Codex-Projects\\hello-Codex`

`codex`

`codex`

`codex --cd 项目路径`

`codex --cd D:\\AI-Codex-Projects\\hello-Codex`

`codex -C 项目路径`

`codex -C ./hello-Codex`

新手推荐最简单的方式：

```
cd 项目目录
codex
```

不要在这些地方直接运行 Codex：

```
C:\
桌面
下载文件夹
系统目录
重要资料文件夹
```

---

###### 登录相关命令

命令 作用 适合场景

`codex login` 默认打开浏览器，用 ChatGPT 账号登录 小白首选 `codex login --device-auth` 用设备码登录 远程服务器、浏览器打不开 `printenv OPENAI_API_KEY | codex login --with-api-key` 使用 API Key 登录 开发者、自动化、CI/CD `codex login status` 查看当前登录方式和状态 不确定是否已登录 `codex logout` 删除本机保存的登录凭证 换账号、公共电脑

`codex login`

`codex login --device-auth`

`printenv OPENAI_API_KEY | codex login --with-api-key`

`codex login status`

`codex logout`

Windows PowerShell 使用 API Key 登录：

```
$env:OPENAI_API_KEY | codex login --with-api-key
```

---

###### 启动时直接发任务

命令 作用 示例

`codex "任务内容"` 启动 Codex，并直接发送第一条任务 `codex "请解释这个项目结构"` `codex -i 图片路径 "任务"` 附加图片一起分析 `codex -i ./error.png "分析这个报错"` `codex --image 图片路径 "任务"` `-i` 的完整写法 `codex --image ./ui.png "根据截图优化页面"` `codex --search "任务"` 允许使用搜索能力 `codex --search "查一下这个库的新用法"`

`codex "任务内容"`

`codex "请解释这个项目结构"`

`codex -i 图片路径 "任务"`

`codex -i ./error.png "分析这个报错"`

`codex --image 图片路径 "任务"`

`-i`

`codex --image ./ui.png "根据截图优化页面"`

`codex --search "任务"`

`codex --search "查一下这个库的新用法"`

适合：

```
简单解释项目
分析报错截图
根据 UI 截图提修改建议
查新版本文档
```

新手更推荐先运行：

```
codex
```

进入后再输入任务，更容易观察执行过程。

---

###### 模型、权限、沙盒相关命令

命令 作用 简单来说 新手建议

`codex --model 模型名` 指定模型 选择 AI 大脑 默认即可，复杂任务再改 `codex -m 模型名` `--model` 简写 更短写法 不必强行记 `codex --sandbox read-only` 只读模式 只能看，尽量不改 只分析项目时用 `codex --sandbox workspace-write` 当前项目可读写 能在项目里工作 日常推荐 `codex --sandbox danger-full-access` 完全放开限制 权限很大 新手不要用 `codex --ask-for-approval on-request` 敏感操作先问你 请求批准 新手推荐 `codex -a on-request` 审批模式简写 更短写法 推荐

`codex --model 模型名`

`codex -m 模型名`

`--model`

`codex --sandbox read-only`

`codex --sandbox workspace-write`

`codex --sandbox danger-full-access`

`codex --ask-for-approval on-request`

`codex -a on-request`

新手推荐组合：

```
codex --sandbox workspace-write --ask-for-approval on-request
```

意思是：

```
Codex 可以在当前项目里工作，但敏感操作要先问我。
```

不要把这个当成省事模式：

```
codex --sandbox danger-full-access
```

---

###### 非交互式任务命令

命令 作用 简单来说 适合场景

`codex exec "任务"` 一次性执行任务 不进入长对话，跑完就结束 自动化、检查、生成报告 `codex e "任务"` `exec` 的简写 同上 快速执行 `codex exec --cd 项目路径 "任务"` 指定目录执行任务 在某个项目里一次性执行 自动化脚本 `codex exec resume` 恢复 exec 会话 接着上次非交互任务继续 自动化任务中断后 `codex exec resume --last` 恢复最近一次 exec 会话 接着最近任务继续 最常用恢复方式

`codex exec "任务"`

`codex e "任务"`

`exec`

`codex exec --cd 项目路径 "任务"`

`codex exec resume`

`codex exec resume --last`

示例：

```
codex exec "请检查当前项目有没有明显问题"
```

小白阶段优先用：

```
codex
```

熟悉后再用 `codex exec`。

---

###### 会话管理命令

命令 作用 简单来说 使用场景

`codex resume` 恢复之前会话 接着之前的 thread 继续 上次没做完 `codex resume --last` 恢复最近一次会话 接着最近任务继续 最常用 `codex archive` 归档会话 把不用的任务收起来 任务完成或不要了 `codex unarchive` 恢复归档会话 找回被归档的任务 归档后还想继续 `codex fork` 复制旧会话成新 thread 保留原任务，再试一个新方向 多方案尝试

`codex resume`

`codex resume --last`

`codex archive`

`codex unarchive`

`codex fork`

简单来说：

```
resume = 接着做
archive = 收起来
unarchive = 找回来
fork = 复制一份去试新方案
```

---

###### 诊断、更新和维护命令

命令 作用 什么时候用

`codex doctor` 生成诊断报告 Codex 启动异常、登录异常、环境异常 `codex update` 检查并更新 Codex CLI 想升级版本时 `codex completion` 生成命令补全脚本 经常用终端的人 `codex features list` 查看功能开关 排查功能是否开启 `codex features enable 功能名` 开启某个功能 进阶配置 `codex features disable 功能名` 关闭某个功能 进阶配置

`codex doctor`

`codex update`

`codex completion`

`codex features list`

`codex features enable 功能名`

`codex features disable 功能名`

小白最常用：

```
codex doctor
codex update
```

其他先不用记。

---

###### Cloud、MCP、插件相关命令

命令 作用 小白是否需要

`codex cloud` 在终端里浏览或执行 Codex Cloud 任务 暂时不用 `codex apply` 把 Codex Cloud 生成的 diff 应用到本地 用 Cloud 后再学 `codex mcp list` 查看 MCP 工具 暂时不用 `codex mcp add` 添加 MCP server 进阶 `codex mcp remove` 删除 MCP server 进阶 `codex plugin list` 查看插件 暂时不用 `codex plugin add` 安装插件 进阶 `codex plugin remove` 删除插件 进阶

`codex cloud`

`codex apply`

`codex mcp list`

`codex mcp add`

`codex mcp remove`

`codex plugin list`

`codex plugin add`

`codex plugin remove`

小白阶段先不用管这些。

等你开始用：

```
Codex Cloud
外部工具
数据库
Figma
项目管理工具
MCP
插件
```

再学习这一类命令。

---

###### 沙盒测试命令

命令 作用 适合谁

`codex sandbox` 在 Codex 的沙盒规则下运行命令 进阶用户 `codex sandbox --cd 项目目录 -- 命令` 指定目录运行沙盒命令 调试权限问题 `codex execpolicy` 检查某条命令会被允许、询问还是阻止 进阶安全配置

`codex sandbox`

`codex sandbox --cd 项目目录 -- 命令`

`codex execpolicy`

小白阶段不用学。

只要记住：

```
默认用 workspace-write + on-request。
不要随便 full access。
```

---

###### 危险命令和危险参数

命令 / 参数 为什么危险 新手建议

—sandbox danger-full-access 放开文件和网络限制 不要用 —dangerously-bypass-approvals-and-sandbox 跳过审批和沙盒 不要用 —yolo 上面那个危险参数的别名 不要用 —ask-for-approval never Codex 操作时不再问你 新手不要用 sudo 可能修改系统级内容 不懂不要允许 rm -rf 可能删除大量文件 高危 git reset —hard 可能丢失未保存改动 先确认 git clean -fd 可能删除未跟踪文件 先确认 curl xxx | sh 下载脚本并直接执行 高危

看到这些内容，先问 Codex：

```
请解释这条命令的作用、风险，以及有没有更安全的替代方案。
```

---

###### 新手最推荐记住的命令

排名 命令 为什么重要

1 Codex 启动 Codex CLI 2 `codex login` 登录账号 3 `codex login status` 检查登录状态 4 `codex doctor` 排查环境问题 5 `codex --version` 查看版本 6 `codex resume --last` 接着上次任务继续 7 `codex archive` 归档不用的任务 8 `codex update` 更新 Codex 9 `codex exec "任务"` 一次性执行任务 10 `codex logout` 退出登录

`codex login`

`codex login status`

`codex doctor`

`codex --version`

`codex resume --last`

`codex archive`

`codex update`

`codex exec "任务"`

`codex logout`

---

###### 推荐新手工作流

步骤 命令 目的

1 cd 项目目录 进入项目文件夹 2 git status 看当前项目状态 3 Codex 启动 Codex CLI 4 输入任务 让 Codex 开始工作 5 /diff 在 Codex 内查看改动 6 git diff 在 Git 里再检查一次 7 git add . 暂存满意的修改 8 git commit -m “说明” 保存一个版本 9 `codex archive` 或 `/quit` 归档任务或退出

`codex archive`

`/quit`

##### CLI 斜杠命令

它不是在外面的 PowerShell / Terminal 里输入，而是在进入 Codex 后，在 Codex 输入框里输入 `/` 使用。

###### 小白最常用命令

命令 作用 简单来说 使用场景

/model 切换模型和推理强度 换 AI 大脑和思考深度 任务太难、太慢或想省额度时 /permissions 调整权限 控制 Codex 能不能改文件、联网、运行命令 想收紧或放宽权限时 /diff 查看代码改动 看 Codex 到底改了什么 Codex 修改文件后必看 /plan 进入计划模式 先让 Codex 给方案，不急着改代码 复杂任务、修 bug、重构前 /init 生成 AGENTS.md 创建项目规则文件 新项目第一次使用 Codex 时 /status 查看当前状态 看模型、权限、上下文、token 等信息 不确定当前配置时 /quit 退出 Codex CLI 结束当前会话 任务完成后退出 /exit 退出 Codex CLI 和 /quit 类似 任务完成后退出

---

###### 模型与速度相关

命令 作用 什么时候用

/model 选择模型和推理强度 想切换 GPT-5.5、mini、低/中/高推理时 /fast 开启或关闭 Fast 模式 想让支持的模型更快响应时 /personality 调整回答风格 想让 Codex 更简洁、更解释型或更协作时 /status 查看当前模型和上下文状态 想确认现在到底用的是什么模型时

初学建议：

```
普通任务：默认模型 + 中推理
复杂 bug：高推理
简单改文案：低推理
不要所有任务都开最高推理
```

---

###### 权限与安全相关

命令 作用 简单来说 建议

/permissions 修改权限策略 控制 Codex 能做什么 新手保持“请求批准” /approve 批准一次被自动拒绝的操作 让被拦截的操作重试一次 看懂风险后再用 /sandbox-add-read-dir 额外允许读取某个目录 让 Codex 能读项目外指定目录 Windows 特定场景，少用 /status 查看权限和可写目录 确认 Codex 当前权限范围 改权限后检查一下

初学建议：

```
默认用 /permissions 保持请求批准。
不要随便放开完全访问权限。
看不懂的操作，不要用 /approve。
```

---

###### 代码检查与 Review 相关

命令 作用 简单来说 使用场景

/diff 查看当前 Git diff 看新增了什么、删除了什么 修改后必看 /review 让 Codex review 当前改动 让它检查代码有没有问题 提交前检查 /copy 复制最近一次 Codex 输出 快速复制结果 复制计划、总结、命令说明 /raw 切换原始输出模式 方便复制长日志或终端输出 日志很长时

推荐流程：

```
Codex 修改完成
→ /diff 查看改动
→ /review 检查问题
→ 没问题再 git commit
```

---

###### 会话管理相关

命令 作用 简单来说 使用场景

/new 开始新对话 在当前 CLI 里换一个新任务 当前任务结束，想开始新任务 /clear 清空终端并开始新聊天 清理当前显示和上下文 界面太乱、想重新开始 /resume 恢复之前的会话 接着以前的任务继续 上次任务没做完 /archive 归档当前会话并退出 把不用的任务收起来 任务完成或方案不要了 /fork 复制当前会话成新 thread 保留原思路，另开分支尝试 想试另一个方案 /side 开一个临时侧边对话 不影响主任务地问个小问题 想临时确认一个点 /quit 退出 CLI 结束当前使用 任务完成 /exit 退出 CLI 和 /quit 一样 任务完成

小白区别：

```
/new = 开新任务
/clear = 清理并重新开始
/archive = 收起当前任务
/fork = 复制当前任务去试新方案
/side = 临时问个小问题
```

---

###### 上下文与长对话相关

命令 作用 简单来说 使用场景

/compact 压缩当前对话 把长对话总结成重点 对话很长、上下文快满时 /status 查看上下文使用情况 看还有多少上下文空间 任务做了很多轮后 /mention 附加文件或文件夹 指定 Codex 重点看某个文件 想让它只看某几个文件 /ide 引入 IDE 当前上下文 把编辑器打开的文件带进来 配合 VS Code / Cursor 使用

初学建议：

```
对话长了用 /compact。
想让 Codex 看特定文件，用 /mention。
不想让它乱扫整个项目，就明确指定文件。
```

---

###### 项目规则与能力相关

命令 作用 简单来说 使用场景

/init 生成 AGENTS.md 创建项目规则文件 新项目第一次用 Codex /skills 浏览和使用 Skills 选择专项技能 做 UI、写文档、review 等专项任务 /memories 配置记忆 控制 Codex 是否使用或生成记忆 想管理长期偏好时 /goal 设置任务目标 给 Codex 一个持续目标 大任务、长任务 /apps 浏览可连接的应用 让 Codex 使用外部 App 连接外部工具时 /plugins 管理插件 查看或启用插件能力 需要插件工具时 /mcp 查看 MCP 工具 看 Codex 能调用哪些外部工具 配置 MCP 后检查

新手优先掌握：

```
/init
/skills
```

其他命令可以后面再学。

---

###### 终端和后台任务相关

命令 作用 简单来说 使用场景

/ps 查看后台终端任务 看哪些命令还在跑 npm dev、测试、构建还在运行时 /stop 停止后台终端任务 终止正在后台跑的命令 命令卡住或不想继续跑 /raw 原始输出模式 方便复制终端日志 日志很长时

常见场景：

```
Codex 跑了 npm run dev
你想看它还在不在跑
→ 用 /ps

命令卡住了
→ 用 /stop
```

---

###### 界面与快捷键相关

命令 作用 简单来说 是否常用

/theme 切换代码高亮主题 改终端显示风格 一般 /statusline 配置底部状态栏 显示模型、token、Git 分支等 进阶 /title 配置终端标题 让窗口标题显示项目信息 进阶 /keymap 修改快捷键 自定义操作按键 进阶 /vim 开关 Vim 编辑模式 用 Vim 方式编辑输入框 会 Vim 的人用 /debug-config 查看配置层级 排查配置为什么不生效 进阶排错

小白阶段可以先不用这些。

---

###### 开发者和高级功能

命令 作用 适合谁

/experimental 开启实验功能 喜欢尝鲜的用户 /hooks 查看和管理生命周期 hooks 高级用户、团队项目 /feedback 发送日志或反馈 遇到问题需要反馈时 /agent 切换 active agent thread 使用 subagent 工作流的人

这些不是入门必学内容。

新手知道有就行，不需要一开始掌握。

---

###### 新手最推荐记住的 8 个

排名 命令 为什么重要

1 /diff 看 Codex 实际改了什么 2 /plan 复杂任务先让它给计划 3 /permissions 控制权限，避免乱改 4 /model 切换模型和推理强度 5 /status 查看当前模型、权限、上下文 6 /init 生成项目规则 7 /compact 长对话压缩重点 8 /quit 退出 Codex

---

###### 推荐新手使用流程

步骤 命令 目的

1 /init 生成项目规则 2 /permissions 确认权限不要太大 3 /model 确认模型和推理强度 4 /plan 复杂任务先规划 5 输入任务 让 Codex 开始工作 6 /diff 检查代码改动 7 /review 让 Codex 再检查一遍 8 /status 查看当前状态和上下文 9 /compact 对话太长时压缩 10 /quit 退出 Codex

---

###### 一句话总结

Slash Commands 是 Codex CLI 里的快捷控制命令。

新手不用全部背，先记住这几个就够了：

```
/diff       看改动
/plan       先规划
/permissions 控权限
/model      换模型
/status     看状态
/init       建规则
/compact    压缩长对话
/quit       退出
```

#### CLI 工作方式

Codex CLI 的工作方式，可以理解成一条完整流程：

```
读取项目
→ 理解任务
→ 提出计划
→ 修改文件
→ 运行命令
→ 等待批准
→ 展示 diff
→ 处理失败
```

小白不用一开始理解所有技术细节，只要先知道：

Codex CLI 不是只会聊天，它会真的进入当前项目目录，读文件、改文件、跑命令，然后把结果展示给你检查。

---

###### Codex 如何读取项目

当你在项目目录里运行：

```
codex
```

Codex 会把当前目录当成工作区。

比如你在这个目录里启动：

```
D:\AI-Codex-Projects\hello-codex
```

Codex 就会围绕这个文件夹里的内容工作。

它可能会读取：

内容 作用

项目文件 理解当前代码 文件夹结构 判断项目是前端、后端还是脚本项目 package.json 判断启动命令、依赖、项目类型 README.md 理解项目说明 AGENTS.md 读取你给 Codex 写的工作规则 报错日志 分析问题原因 Git 状态 判断哪些文件被改过

简单来说：

```
你在哪个文件夹启动 Codex，
Codex 就默认把哪个文件夹当成当前项目。
```

所以不要在这些地方乱启动：

```
C:\
桌面
下载文件夹
系统目录
重要资料文件夹
```

推荐做法：

```
cd 项目目录
codex
```

---

###### Codex 如何理解任务

你输入任务后，Codex 会先判断你想让它做什么。

比如你输入：

```
请帮我做一个简单网页，黑色背景，中间显示 Hello Codex。
```

Codex 会判断：

它会理解什么 示例

任务类型 新建网页 修改范围 当前项目文件 可能需要文件 index.html、style.css 是否需要运行命令 简单 HTML 不一定需要 是否有风险 风险较低

如果你输入：

```
请检查为什么 npm run build 失败。
```

Codex 会判断：

它会理解什么 示例

任务类型 排查构建失败 可能要运行命令 npm run build 可能要读文件 package.json、报错相关文件 是否需要修改代码 可能需要 是否需要你批准 视权限设置而定

小白提示：

任务越清楚，Codex 越稳定。

推荐写法：

```
请帮我完成【具体任务】。

要求：
1.
2.
3.

限制：
1. 不要修改无关文件
2. 不要删除已有功能
3. 完成后告诉我改了哪些文件
```

---

###### Codex 如何提出计划

复杂任务开始前，Codex 通常会先分析问题，再提出计划。

你也可以主动要求它先计划：

```
请先给我计划，不要直接修改文件。
```

或者使用：

```
/plan
```

计划通常会包含：

内容 作用

它准备检查哪些文件 防止乱扫项目 它准备怎么修改 让你先知道方向 它可能运行什么命令 提前了解风险 它预计影响哪些地方 方便你判断是否接受

比如：

```
计划：
1. 先查看 package.json，确认启动命令
2. 运行 npm run build 复现报错
3. 根据报错定位相关文件
4. 最小范围修复问题
5. 再次运行 build 验证
```

初学建议：

```
简单任务可以直接让它做。
复杂任务先让它 /plan。
```

尤其是这些任务，建议先计划：

```
修复复杂 bug
多文件修改
项目重构
新增功能
构建失败
涉及依赖升级
```

---

###### Codex 如何修改文件

当 Codex 确认要修改文件后，它会在当前项目里进行编辑。

它可能会：

操作 示例

新建文件 新建 index.html 修改文件 修改 style.css 删除代码 删除无用代码 重命名文件 调整文件名 拆分文件 把代码拆成多个模块

新手要注意：

Codex 可能会改对，也可能会改多。

所以你要养成习惯：

```
它改完之后，不要直接相信。
一定要看 diff。
```

你可以提前加限制：

```
请只修改 index.html 和 style.css，不要修改其他文件。
```

或者：

```
请用最小改动修复问题，不要重构整个项目。
```

这样可以减少 Codex 改动范围过大的问题。

---

###### Codex 如何运行命令

Codex 不只会改文件，也可以运行终端命令。

常见命令包括：

命令 作用

npm install 安装依赖 npm run dev 启动开发项目 npm run build 检查项目能否构建 npm test 运行测试 git status 查看 Git 状态 git diff 查看代码改动

比如你让它修构建失败，它可能会运行：

```
npm run build
```

然后根据报错继续修改。

小白不要害怕命令，但要看懂再允许。

如果你不懂，可以让它先解释：

```
请先解释你准备运行的命令，每条命令是干什么的，不要直接执行。
```

尤其看到这些命令，要谨慎：

```
rm -rf
sudo
curl xxx | sh
git reset --hard
git clean -fd
```

这些命令可能删除文件、修改系统、重置代码或执行远程脚本。

---

###### Codex 如何等待用户批准

Codex CLI 有权限控制，不是所有操作都能直接执行。

如果 Codex 想做敏感操作，可能会停下来问你。

比如：

操作 为什么可能需要批准

联网安装依赖 可能下载外部代码 访问项目外文件 超出当前工作区 修改外部文件 可能影响其他项目 运行高风险命令 可能删除或覆盖内容 使用更高权限 风险更大

简单来说：

```
批准 = 你允许 Codex 继续做这一步。
拒绝 = 这一步不要做。
```

如果你看不懂它要做什么，不要直接点允许。

可以先问：

```
请解释这个操作的作用、风险，以及有没有更安全的替代方案。
```

新手建议权限：

```
保持请求批准。
不要随便开启完全访问权限。
```

---

###### Codex 如何展示 diff

Diff 是 Codex 修改前后的代码对比。

你可以在 Codex CLI 里输入：

```
/diff
```

它会展示当前改动。

简单来说：

```
绿色 = 新增内容
红色 = 删除内容
```

diff 可以帮你确认：

检查点 你要看什么

是否改了正确文件 有没有改到无关文件 是否删除重要代码 红色删除部分要重点看 是否新增复杂依赖 有没有多装不必要的包 是否改动太大 小任务不要变成大重构 是否符合需求 有没有实现你要求的效果

推荐流程：

```
Codex 完成修改
→ 输入 /diff
→ 查看改动
→ 不满意就让它继续改或撤回
→ 满意后再 git commit
```

不要只看 Codex 的总结。

真正重要的是：

```
它实际改了什么。
```

---

###### Codex 如何处理失败

Codex 执行任务失败很正常。

常见失败包括：

失败类型 示例

命令失败 npm run build 报错 依赖缺失 没有安装某个包 代码报错 页面空白、函数报错 权限不足 没有联网或文件访问权限 理解错需求 改的不是你想要的 修改范围过大 顺手改了无关文件

Codex 通常会根据失败结果继续分析。

比如：

```
运行 npm run build 失败
→ 读取报错信息
→ 定位相关文件
→ 修改代码
→ 再次运行 build
```

但你要注意：

不要让它无限乱试。

如果它连续失败，可以暂停它，让它重新分析：

```
先停一下。请总结目前失败原因，不要继续修改文件。
```

或者：

```
请列出你已经尝试过的方法、失败原因，以及下一步最小改动方案。
```

如果它改乱了，可以说：

```
请撤回刚才的修改，恢复到修改前状态。
```

或者自己用 Git 查看：

```
git status
git diff
```

再决定是否保留。

---

###### 推荐新手工作流

步骤 操作 目的

1 cd 项目目录 进入正确项目 2 Codex 启动 Codex CLI 3 输入任务 告诉 Codex 要做什么 4 复杂任务先 /plan 先看方案 5 等 Codex 读取项目 让它理解上下文 6 审批敏感操作 看懂再允许 7 等它修改文件 执行任务 8 运行命令检查 验证结果 9 /diff 查看改动 10 不满意继续修改 迭代优化 11 满意后 git commit 保存版本

---

###### 一句话总结

Codex CLI 的工作方式不是“问一句答一句”，而是一个完整的编程流程：

```
读项目
→ 想方案
→ 改文件
→ 跑命令
→ 等批准
→ 看 diff
→ 修失败
→ 交结果
```

#### CLI 常见问题

Codex CLI 常见问题，大多数不是 Codex 本身坏了，而是出在这几个地方：

##### 小白最常见问题

问题 常见原因 解决方法

输入 `codex` 没反应 Codex 没装好，或命令没加入环境变量 先运行 `codex --version` 检查 提示 command not found 终端找不到 Codex 命令 重新安装 Codex CLI，或重开终端 不知道在哪运行 Codex 没进入项目目录 先 cd 项目目录，再运行 Codex Codex 读错项目 在错误文件夹启动了 退出后进入正确项目目录重新启动 登录失败 浏览器没打开、网络异常、账号没登录 使用 `codex login` 重新登录 API Key 登录失败 Key 没设置、Key 错误、环境变量没生效 重新设置环境变量后再登录 Codex 一直等待 可能在等你批准权限 看终端是否有 approval 提示 Codex 不能联网 沙盒或权限限制 需要联网时手动批准 改完不知道改了什么 没看 diff 在 Codex 里输入 /diff 改坏了怎么办 没提前用 Git 保存 用 git diff 检查，必要时 revert

`codex`

`codex --version`

`codex login`

---

##### 安装类问题

问题 原因 解决方法

`codex --version` 没有输出 Codex 没安装成功 重新安装 Codex CLI `codex: command not found` 命令没有加入 PATH 重开终端，或重新安装 npm 安装失败 Node.js / npm 没装好 先运行 node -v 和 npm -v Windows 安装后找不到命令 PowerShell 没刷新环境变量 关闭终端，重新打开 版本太旧 Codex CLI 没更新 运行 `codex update` 或重新安装

`codex --version`

`codex: command not found`

`codex update`

排查命令：

```
codex --version
node -v
npm -v
codex doctor
```

初学建议：

```
安装后第一件事，不是直接用，而是先运行 codex --version。
能看到版本号，说明基础安装正常。
```

---

##### 登录类问题

问题 原因 解决方法

不知道有没有登录 没检查登录状态 运行 `codex login status` 浏览器没有自动打开 默认浏览器异常或远程环境 使用 `codex login --device-auth` ChatGPT 登录失败 网络、账号、浏览器缓存问题 重新运行 `codex login` API Key 登录失败 环境变量没设置好 检查 OPENAI_API_KEY 想换账号 本机保存了旧账号 先 `codex logout`，再重新登录

`codex login status`

`codex login --device-auth`

`codex login`

`codex logout`

常用命令：

```
codex login
codex login status
codex logout
codex login --device-auth
```

初学建议：

```
本地学习优先用 ChatGPT 账号登录。
API Key 登录更适合开发者、自动化和服务器场景。
```

---

##### 项目目录类问题

问题 原因 解决方法

Codex 看不到项目文件 没进入项目目录 先 cd 项目目录 Codex 读错文件 在错误目录启动 退出后重新进入正确目录 Codex 扫描了太多东西 在桌面、下载目录或 C 盘启动 只在具体项目文件夹里启动 不知道当前在哪 不清楚终端所在路径 Windows 用 cd，Mac 用 pwd 找不到文件 文件不在当前项目内 用 /mention 指定文件，或进入正确目录

推荐方式：

```
cd D:\AI-Codex-Projects\hello-codex
codex
```

不推荐：

```
在 C 盘根目录运行
在桌面运行
在下载文件夹运行
在重要资料文件夹运行
```

一句话：

```
你在哪个目录运行 codex，它就默认把哪个目录当成项目。
```

---

##### 权限和沙盒类问题

问题 原因 解决方法

Codex 提示需要批准 它要执行敏感操作 看懂后再允许 Codex 不能访问网络 沙盒默认限制联网 需要时手动批准 Codex 不能读取项目外文件 超出 workspace 范围 不建议随便放开 Codex 不能修改某些文件 权限不足或在只读模式 检查 /permissions Codex 请求完全访问权限 任务需要更大权限 小白不要随便同意

推荐设置：

```
sandbox：workspace-write
approval：on-request
```

简单来说：

```
workspace-write = 允许在当前项目里工作
on-request = 敏感操作先问你
```

不要随便使用：

```
danger-full-access
--yolo
--dangerously-bypass-approvals-and-sandbox
```

看到不懂的权限请求，可以问：

```
请解释这个操作为什么需要权限，会影响哪些文件，有没有更安全的替代方案。
```

---

##### 命令运行类问题

问题 原因 解决方法

npm run dev 失败 依赖没装或脚本不存在 先看 package.json npm install 失败 网络、源、权限或依赖冲突 让 Codex 先分析错误 npm run build 失败 项目代码本身有报错 让 Codex 复现并最小修复 命令卡住不动 开发服务器一直运行 用 /ps 查看后台任务 想停止命令 命令一直占用终端 用 /stop 停止后台任务

常见命令含义：

命令 含义

npm install 安装项目依赖 npm run dev 启动开发环境 npm run build 检查项目能否正式构建 npm test 运行测试 git status 查看项目改动状态 git diff 查看具体改动

不懂命令时，先让 Codex 解释：

```
请先解释你准备运行的命令，每条命令是干什么的，不要直接执行。
```

---

##### Diff 和改动类问题

问题 原因 解决方法

不知道 Codex 改了什么 没看 diff 输入 /diff diff 里改动太多 Codex 修改范围过大 要求它最小改动 改了无关文件 任务限制不清楚 让它撤回无关修改 删除了重要代码 没检查红色删除部分 用 Git 恢复或让它 revert /diff 没东西 没有文件改动，或改动已保存处理 用 git status 再检查

推荐检查流程：

```
Codex 完成任务
→ 输入 /diff
→ 看改了哪些文件
→ 看红色删除部分
→ 看是否改了无关文件
→ 满意后再 git commit
```

提示词可以这样写：

```
请只修改当前任务相关文件。
不要重构整个项目。
完成后列出修改了哪些文件。
```

---

##### Git 相关问题

问题 原因 解决方法

改坏了不知道怎么恢复 没用 Git 保存版本 以后先 git init 和 commit git status 显示很多文件 Codex 或你自己改了很多内容 用 git diff 逐个检查 不知道哪些改动要保留 没看 diff 先不要 commit commit 后想回退 Git 基础不熟 先让 Codex 解释回退方案 Codex 改了不该改的文件 任务范围太大 要求它 revert 无关文件

推荐新手第一次项目先做：

```
git init
git add .
git commit -m "initial commit"
```

之后 Codex 每次改完：

```
git status
git diff
```

简单来说：

```
git status = 看哪些文件变了
git diff = 看具体变了什么
commit = 保存一个版本
```

---

##### 模型和额度类问题

问题 原因 解决方法

某个模型看不到 套餐、地区或权限不同 使用当前可选模型 任务变慢 模型强、推理高、项目大 降低推理或缩小任务范围 额度消耗太快 高推理、多轮修改、读大项目 小任务用低/中推理 提示达到限制 当前计划额度用完 等额度恢复或购买额外额度 API Key 消耗费用 API 登录按 API 使用计费 小白优先用 ChatGPT 登录

省额度建议：

```
小任务不要开最高推理。
不要一次让 Codex 扫整个项目。
不要反复让它大范围重构。
能指定文件就指定文件。
复杂任务先 /plan，再修改。
```

推荐配置：

```
普通任务：默认模型 + 中推理
复杂 bug：高推理
小改动：低推理
```

---

##### Codex 卡住或结果不对

问题 原因 解决方法

Codex 一直不动 等待权限、命令卡住、任务太大 检查是否有 approval 或 /ps Codex 反复修不好 没找到根因 让它先总结失败原因 Codex 越改越乱 没限制修改范围 暂停，要求最小改动 Codex 理解错需求 任务描述太模糊 重新写清楚目标、要求、限制 输出太长太乱 对话上下文太长 使用 /compact

可以这样叫停：

```
先停一下，不要继续修改文件。
请总结目前做了什么、失败在哪里、下一步最小修改方案是什么。
```

如果它改偏了，可以说：

```
这次方向不对。请撤回刚才的无关修改，只保留和首页样式相关的改动。
```

---

##### Windows 常见问题

问题 原因 解决方法

PowerShell 不识别 Codex 环境变量未刷新 关闭终端重新打开 路径带空格报错 路径没有加引号 用英文路径或加引号 API Key 命令不适用 Windows 和 Mac 命令不同 用 PowerShell 写法 权限弹窗频繁 Windows 安全限制或沙盒审批 保持请求批准即可 中文路径异常 某些工具对中文路径兼容不好 项目路径尽量用英文

推荐 Windows 项目路径：

```
D:\AI-Codex-Projects\hello-codex
```

不推荐：

```
C:\Users\你的名字\桌面\新建文件夹
```

原因：

```
中文路径、空格、桌面目录，有时更容易出问题。
```

---

##### macOS 常见问题

问题 原因 解决方法

提示权限不足 文件夹权限限制 换到用户目录下的项目文件夹 命令找不到 PATH 没生效 重开 Terminal npm 权限问题 全局安装权限问题 优先用官方推荐安装方式 浏览器登录没跳回终端 浏览器拦截或网络问题 用 device auth 终端不熟悉路径 不知道当前目录 用 pwd 和 ls

推荐项目路径：

```
~/AI-Codex-Projects/hello-codex
```

常用检查命令：

```
pwd
ls
codex --version
codex doctor
```

---

##### 运行 `codex doctor` 排查

如果你不知道问题出在哪里，可以先运行：

```
codex doctor
```

它适合排查：

```
安装异常
登录异常
配置异常
终端环境异常
权限问题
系统环境问题
```

简单来说：

```
codex doctor = Codex 的体检命令。
```

遇到复杂问题时，可以把 doctor 结果发给 Codex，让它帮你分析：

```
请根据 codex doctor 的输出，帮我判断 CLI 哪里有问题。
```

---

##### 新手通用排查流程

步骤 命令 / 操作 目的

1 `codex --version` 检查是否安装成功 2 `codex login status` 检查是否登录 3 pwd / cd 确认当前项目目录 4 git status 查看项目状态 5 `codex doctor` 检查环境问题 6 /permissions 检查权限设置 7 /diff 查看文件改动 8 /ps 查看后台任务 9 /stop 停止当前任务 10 /compact 对话太长时压缩上下文

`codex --version`

`codex login status`

`codex doctor`

---

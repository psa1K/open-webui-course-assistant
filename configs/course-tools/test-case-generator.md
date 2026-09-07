# 编程题测试用例生成工具

## 用途

`编程题测试用例生成工具`（Tool ID：`test_case_generator`）是一个 Open WebUI Workspace Tool，输入题目描述/模板，输出**真实可运行的测试用例数据**（`输入 / 期望输出` 对），非占位或模拟数据。

两种模式：

1. **内置模板** `generate_test_cases`：7 个课程相关算法模板（KMP 前缀函数、KMP 模式匹配、阶乘、斐波那契、最大公约数、两数之和、最大子数组和），每个带**真实参考实现**，生成随机合法输入并运行参考解算出期望输出。
2. **自定义参考解** `generate_with_reference`：调用方提供题目描述 + 参考解（Python，定义 `def solve(data)`）+ 输入规格，工具生成输入并在**受限命名空间**中运行参考解算出期望输出。

## 真实可运行的关键

- 期望输出由**真实参考实现计算**得到，而非模型猜测或占位符
- 参考解在**受限命名空间**中执行：仅暴露安全的纯函数内建（`len`/`range`/`min`/`max`/`sum`/`sorted` 等），无 `open`/`import`/`__import__`/`eval`/`exec`/`subprocess`——无法访问文件系统、网络或执行系统命令
- 支持 `seed` 复现；测试用例全部 JSON 可序列化

## 内置模板清单（`list_problems`）

| key | 名称 | 输入 | 期望输出 |
|---|---|---|---|
| `prefix_function` | KMP 前缀函数 | 字符串 | pi 数组 |
| `kmp_search` | KMP 模式匹配 | pattern+text | 出现位置列表 |
| `factorial` | 阶乘 | 整数 n | n! |
| `fibonacci` | 斐波那契数列 | 整数 n | F(n) |
| `gcd` | 最大公约数 | a, b | gcd(a,b) |
| `two_sum` | 两数之和 | nums+target | 两个下标 |
| `max_subarray_sum` | 最大子数组和 | 整数数组 | 最大和 |

## 输入参数

| 参数 | 类型 | 约束 |
|---|---|---|
| `problem_key` | `string` | `generate_test_cases` 必填，须为内置模板 key |
| `problem` | `string` | `generate_with_reference` 必填，题目描述 |
| `reference_code` | `string` | 自定义参考解，须含 `def solve(data)` |
| `input_spec` | `string` | 输入规格 JSON，如 `{"kind":"int","min":1,"max":100}` |
| `count` | `integer` | 1–20，默认 5 |
| `seed` | `integer \| null` | 可选，复现用 |
| `constraints` | `string` | `generate_test_cases` 可选，覆盖模板默认输入范围 |

输入规格 `kind` 支持：`int` / `int_pair` / `int_list` / `str` / `two_sum` / `kmp`。

## 输出结构

```json
{
  "status": "ok",
  "mode": "test_case_generation",
  "problem": {"key": "gcd", "name": "最大公约数", "description": "…"},
  "count": 3,
  "seed": 42,
  "test_cases": [
    {"input": {"a": 164, "b": 29}, "expected_output": 1}
  ]
}
```

## Open WebUI 使用

```bash
# 安装/更新（校验 + 上传）
.venv/bin/python scripts/create_test_case_generator_tool.py --dry-run
.venv/bin/python scripts/create_test_case_generator_tool.py
```

对话中直接说：

```text
用测试用例生成工具，生成 5 组两数之和的测试用例，seed=1。
```

```text
用我的参考解 def solve(data): return data**2 生成 3 组测试用例，输入是 1 到 10 的整数。
```

## 学术诚信与安全

- 期望输出为确定性参考解计算结果，仅用于自检与评测
- 自定义参考解在受限命名空间运行，无法读取文件/联网/执行系统命令；若参考解无法产生任何结果，返回 `REFERENCE_ERROR` 而非崩溃
- 工具不联网、不访问数据库、不含密钥
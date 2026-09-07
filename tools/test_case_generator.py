"""Open WebUI Workspace Tool: generate runnable test cases for programming problems.

Two modes:
  - generate_test_cases: use a built-in problem template (course-relevant
    algorithms such as KMP prefix function, pattern search, classic coding
    problems). Generates random valid inputs and computes the expected output
    with a real reference implementation.
  - generate_with_reference: caller supplies a reference solution (Python,
    defining `solve(data)`) plus an input spec; the tool generates inputs and
    runs the reference in a restricted namespace to compute expected outputs.

Test cases are real runnable data (input / expected_output pairs), not mocks.
"""
from __future__ import annotations

import json
import random
import re
from typing import Any

MAX_COUNT = 20

SAFE_BUILTINS = {
    "abs": abs,
    "all": all,
    "any": any,
    "bool": bool,
    "dict": dict,
    "divmod": divmod,
    "enumerate": enumerate,
    "float": float,
    "int": int,
    "len": len,
    "list": list,
    "max": max,
    "min": min,
    "pow": pow,
    "range": range,
    "reversed": reversed,
    "round": round,
    "set": set,
    "sorted": sorted,
    "str": str,
    "sum": sum,
    "tuple": tuple,
    "zip": zip,
}


def _prefix_function(s: str) -> list[int]:
    pi = [0] * len(s)
    k = 0
    for q in range(1, len(s)):
        while k > 0 and s[k] != s[q]:
            k = pi[k - 1]
        if s[k] == s[q]:
            k += 1
        pi[q] = k
    return pi


def _kmp_search(pattern: str, text: str) -> list[int]:
    pi = _prefix_function(pattern)
    positions = []
    q = 0
    for i, ch in enumerate(text):
        while q > 0 and pattern[q] != ch:
            q = pi[q - 1]
        if pattern[q] == ch:
            q += 1
        if q == len(pattern):
            positions.append(i - len(pattern) + 1)
            q = pi[q - 1]
    return positions


def _factorial(n: int) -> int:
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def _fibonacci(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def _gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return abs(a)


def _two_sum(nums: list[int], target: int) -> list[int]:
    seen: dict[int, int] = {}
    for i, value in enumerate(nums):
        need = target - value
        if need in seen:
            return [seen[need], i]
        seen[value] = i
    return []


def _max_subarray_sum(nums: list[int]) -> int:
    best = current = 0
    for value in nums:
        current = max(value, current + value)
        best = max(best, current)
    return best


def _merge(base: dict[str, Any], overrides: dict[str, Any] | None) -> dict[str, Any]:
    merged = dict(base)
    for key, value in (overrides or {}).items():
        merged[key] = value
    return merged


def _rand_int(rng: random.Random, spec: dict[str, Any]) -> int:
    return rng.randint(int(spec.get("min", 0)), int(spec.get("max", 100)))


def _rand_int_list(rng: random.Random, spec: dict[str, Any]) -> list[int]:
    min_len = int(spec.get("min_len", 1))
    max_len = int(spec.get("max_len", 10))
    length = rng.randint(min_len, max_len)
    min_val = int(spec.get("min_val", -100))
    max_val = int(spec.get("max_val", 100))
    return [rng.randint(min_val, max_val) for _ in range(length)]


def _rand_int_pair(rng: random.Random, spec: dict[str, Any]) -> dict[str, int]:
    min_val = int(spec.get("min", 1))
    max_val = int(spec.get("max", 100))
    return {"a": rng.randint(min_val, max_val), "b": rng.randint(min_val, max_val)}


def _rand_str(rng: random.Random, spec: dict[str, Any]) -> str:
    min_len = int(spec.get("min_len", 1))
    max_len = int(spec.get("max_len", 10))
    length = rng.randint(min_len, max_len)
    alphabet = str(spec.get("alphabet", "ab"))
    return "".join(rng.choice(alphabet) for _ in range(length))


def _generate_input(spec: dict[str, Any], rng: random.Random) -> Any:
    kind = spec.get("kind")
    if kind == "int":
        return _rand_int(rng, spec)
    if kind == "int_list":
        return _rand_int_list(rng, spec)
    if kind == "str":
        return _rand_str(rng, spec)
    if kind == "int_pair":
        return _rand_int_pair(rng, spec)
    if kind == "two_sum":
        nums = _rand_int_list(rng, {"min_len": 2, "max_len": 10, "min_val": -50, "max_val": 50, **spec})
        i, j = rng.sample(range(len(nums)), 2)
        target = nums[i] + nums[j]
        return {"nums": nums, "target": target}
    if kind == "kmp":
        alphabet = str(spec.get("alphabet", "ab"))
        pattern = _rand_str(rng, {"min_len": 1, "max_len": 4, "alphabet": alphabet})
        text = _rand_str(rng, {"min_len": 5, "max_len": 12, "alphabet": alphabet})
        return {"pattern": pattern, "text": text}
    raise ValueError(f"不支持的输入类型: {kind}")


PROBLEM_TEMPLATES = {
    "prefix_function": {
        "name": "KMP 前缀函数",
        "description": "给定字符串 s，返回其前缀函数 pi 数组（pi[q] 为 s[0..q] 的最长相等真前后缀长度）。",
        "input_spec": {"kind": "str", "min_len": 1, "max_len": 10, "alphabet": "ab"},
        "solve": _prefix_function,
    },
    "kmp_search": {
        "name": "KMP 模式匹配",
        "description": "给定模式串 pattern 与文本 text，返回 pattern 在 text 中所有出现的起始下标。",
        "input_spec": {"kind": "kmp", "alphabet": "ab"},
        "solve": lambda data: _kmp_search(data["pattern"], data["text"]),
    },
    "factorial": {
        "name": "阶乘",
        "description": "给定非负整数 n，返回 n!。",
        "input_spec": {"kind": "int", "min": 0, "max": 12},
        "solve": _factorial,
    },
    "fibonacci": {
        "name": "斐波那契数列",
        "description": "给定 n，返回第 n 项斐波那契数（F(0)=0，F(1)=1）。",
        "input_spec": {"kind": "int", "min": 0, "max": 30},
        "solve": _fibonacci,
    },
    "gcd": {
        "name": "最大公约数",
        "description": "给定两个整数 a、b，返回它们的最大公约数（欧几里得算法）。",
        "input_spec": {"kind": "int_pair", "min": 1, "max": 200},
        "solve": lambda data: _gcd(data["a"], data["b"]),
    },
    "two_sum": {
        "name": "两数之和",
        "description": "给定整数数组 nums 与目标和 target，返回和为 target 的两个元素下标。",
        "input_spec": {"kind": "two_sum"},
        "solve": lambda data: _two_sum(data["nums"], data["target"]),
    },
    "max_subarray_sum": {
        "name": "最大子数组和",
        "description": "给定整数数组 nums，返回连续子数组的最大和（Kadane 算法，允许空子数组记 0）。",
        "input_spec": {"kind": "int_list", "min_len": 1, "max_len": 10, "min_val": -20, "max_val": 20},
        "solve": _max_subarray_sum,
    },
}


class Tools:
    """Generate runnable test cases (input / expected_output pairs)."""

    def generate_test_cases(
        self,
        problem_key: str,
        count: int = 5,
        seed: int | None = None,
        constraints: str = "{}",
    ) -> dict[str, Any]:
        problem_key = problem_key.strip() if isinstance(problem_key, str) else ""
        template = PROBLEM_TEMPLATES.get(problem_key)
        if template is None:
            return {
                "status": "error",
                "error_code": "UNKNOWN_PROBLEM",
                "message": f"未知题目模板: {problem_key}。可用模板: {sorted(PROBLEM_TEMPLATES)}",
            }
        count = self._normalize_count(count)
        if count is None:
            return {"status": "error", "error_code": "INVALID_INPUT", "message": f"count 必须是 1 到 {MAX_COUNT} 之间的整数。"}
        overrides = self._parse_json(seed, constraints)
        if overrides is None:
            return {"status": "error", "error_code": "INVALID_INPUT", "message": "constraints 必须是非空 JSON 对象。"}

        rng = random.Random(seed) if seed is not None else random.SystemRandom()
        base_spec = template["input_spec"]
        test_cases = []
        for _ in range(count):
            spec = _merge(base_spec, overrides)
            input_data = _generate_input(spec, rng)
            try:
                expected = template["solve"](input_data)
            except (RecursionError, ValueError, ZeroDivisionError, IndexError):
                continue
            test_cases.append({"input": input_data, "expected_output": expected})
        return {
            "status": "ok",
            "mode": "test_case_generation",
            "problem": {"key": problem_key, "name": template["name"], "description": template["description"]},
            "count": len(test_cases),
            "seed": seed,
            "test_cases": test_cases,
        }

    def generate_with_reference(
        self,
        problem: str,
        reference_code: str,
        input_spec: str,
        count: int = 5,
        seed: int | None = None,
    ) -> dict[str, Any]:
        if not isinstance(problem, str) or not problem.strip():
            return {"status": "error", "error_code": "INVALID_INPUT", "message": "problem 描述不能为空。"}
        if not isinstance(reference_code, str) or "def solve(" not in reference_code:
            return {"status": "error", "error_code": "INVALID_INPUT", "message": "reference_code 必须定义 def solve(data) 函数。"}
        count = self._normalize_count(count)
        if count is None:
            return {"status": "error", "error_code": "INVALID_INPUT", "message": f"count 必须是 1 到 {MAX_COUNT} 之间的整数。"}
        spec = self._parse_json(seed, input_spec)
        if spec is None:
            return {"status": "error", "error_code": "INVALID_INPUT", "message": "input_spec 必须是非空 JSON 对象。"}

        namespace = {"__builtins__": SAFE_BUILTINS}
        try:
            exec(reference_code, namespace)
        except Exception as exc:
            return {"status": "error", "error_code": "REFERENCE_ERROR", "message": f"reference_code 执行失败: {exc}"}
        solve = namespace.get("solve")
        if not callable(solve):
            return {"status": "error", "error_code": "REFERENCE_ERROR", "message": "reference_code 未定义可调用的 solve(data)。"}

        rng = random.Random(seed) if seed is not None else random.SystemRandom()
        test_cases = []
        for _ in range(count):
            try:
                input_data = _generate_input(spec, rng)
                expected = solve(input_data)
            except Exception:
                continue
            test_cases.append({"input": input_data, "expected_output": expected})
        if not test_cases:
            return {"status": "error", "error_code": "REFERENCE_ERROR", "message": "参考解无法对任何输入产生结果，请检查 solve(data) 实现。"}
        return {
            "status": "ok",
            "mode": "test_case_generation_with_reference",
            "problem": problem.strip(),
            "count": len(test_cases),
            "seed": seed,
            "test_cases": test_cases,
        }

    def list_problems(self) -> dict[str, Any]:
        problems = [
            {"key": key, "name": t["name"], "description": t["description"]}
            for key, t in PROBLEM_TEMPLATES.items()
        ]
        return {"status": "ok", "mode": "problem_list", "count": len(problems), "problems": problems}

    @staticmethod
    def _normalize_count(count: Any) -> int | None:
        if isinstance(count, bool) or not isinstance(count, int):
            return None
        return count if 1 <= count <= MAX_COUNT else None

    @staticmethod
    def _parse_json(_seed: Any, value: str) -> dict[str, Any] | None:
        if not isinstance(value, str) or not value.strip():
            return None
        try:
            data = json.loads(value)
        except (ValueError, json.JSONDecodeError):
            return None
        return data if isinstance(data, dict) else None

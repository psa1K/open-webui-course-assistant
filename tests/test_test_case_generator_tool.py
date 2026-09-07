import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools/test_case_generator.py"
SCRIPT_PATH = ROOT / "scripts/create_test_case_generator_tool.py"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tool = load(TOOL_PATH, "test_case_generator")
creator = load(SCRIPT_PATH, "create_test_case_generator_tool")


class TestCaseGeneratorBuiltinTests(unittest.TestCase):
    def setUp(self):
        self.instance = tool.Tools()

    def test_tools_class_and_methods(self):
        self.assertTrue(hasattr(tool, "Tools"))
        self.assertTrue(callable(self.instance.generate_test_cases))
        self.assertTrue(callable(self.instance.generate_with_reference))
        self.assertTrue(callable(self.instance.list_problems))

    def test_prefix_function_reference_correct(self):
        r = self.instance.generate_test_cases("prefix_function", count=1, seed=1)
        data = r["test_cases"][0]
        s = data["input"]
        pi = data["expected_output"]
        self.assertEqual(len(pi), len(s))
        for q in range(1, len(s)):
            self.assertTrue(0 <= pi[q] <= q)
        self.assertEqual(pi[0], 0)

    def test_factorial_known_values(self):
        self.assertEqual(tool._factorial(0), 1)
        self.assertEqual(tool._factorial(5), 120)

    def test_fibonacci_known_values(self):
        self.assertEqual(tool._fibonacci(0), 0)
        self.assertEqual(tool._fibonacci(10), 55)

    def test_gcd_known_values(self):
        self.assertEqual(tool._gcd(48, 18), 6)
        self.assertEqual(tool._gcd(0, 5), 5)

    def test_kmp_search_correct(self):
        self.assertEqual(tool._kmp_search("ab", "ababab"), [0, 2, 4])
        self.assertEqual(tool._kmp_search("aa", "aaaa"), [0, 1, 2])

    def test_two_sum_output_valid(self):
        r = self.instance.generate_test_cases("two_sum", count=3, seed=5)
        for data in r["test_cases"]:
            nums = data["input"]["nums"]
            target = data["input"]["target"]
            i, j = data["expected_output"]
            self.assertEqual(nums[i] + nums[j], target)

    def test_seed_reproducible(self):
        a = self.instance.generate_test_cases("two_sum", count=3, seed=7)
        b = self.instance.generate_test_cases("two_sum", count=3, seed=7)
        self.assertEqual(a["test_cases"], b["test_cases"])

    def test_unknown_problem_rejected(self):
        self.assertEqual(self.instance.generate_test_cases("nope")["error_code"], "UNKNOWN_PROBLEM")

    def test_invalid_count_rejected(self):
        for bad in (0, 21, 2.5, True, "x"):
            self.assertEqual(self.instance.generate_test_cases("factorial", count=bad)["error_code"], "INVALID_INPUT")

    def test_constraints_override(self):
        r = self.instance.generate_test_cases("factorial", count=5, seed=1, constraints=json.dumps({"min": 0, "max": 1}))
        for data in r["test_cases"]:
            self.assertIn(data["input"], (0, 1))

    def test_test_cases_are_json_serializable(self):
        r = self.instance.generate_test_cases("kmp_search", count=3, seed=2)
        json.dumps(r["test_cases"])

    def test_list_problems(self):
        r = self.instance.list_problems()
        self.assertEqual(r["status"], "ok")
        self.assertGreaterEqual(r["count"], 5)
        keys = {p["key"] for p in r["problems"]}
        self.assertIn("prefix_function", keys)
        self.assertIn("kmp_search", keys)


class TestCaseGeneratorReferenceTests(unittest.TestCase):
    def setUp(self):
        self.instance = tool.Tools()

    def ref(self, code, spec, **kwargs):
        return self.instance.generate_with_reference("自定义题目", code, json.dumps(spec), **kwargs)

    def test_custom_reference_double(self):
        r = self.ref("def solve(data):\n    return data * 2\n", {"kind": "int", "min": 1, "max": 5}, count=3, seed=1)
        self.assertEqual(r["status"], "ok")
        for data in r["test_cases"]:
            self.assertEqual(data["expected_output"], data["input"] * 2)

    def test_custom_reference_sum_list(self):
        r = self.ref("def solve(data):\n    return sum(data)\n", {"kind": "int_list", "min_len": 1, "max_len": 5, "min_val": 0, "max_val": 10}, count=3, seed=2)
        self.assertEqual(r["status"], "ok")
        for data in r["test_cases"]:
            self.assertEqual(data["expected_output"], sum(data["input"]))

    def test_reference_without_solve_rejected(self):
        r = self.instance.generate_with_reference("x", "x = 1\n", "{}")
        self.assertEqual(r["error_code"], "INVALID_INPUT")

    def test_reference_restricted_no_open(self):
        code = "def solve(data):\n    return open('/etc/passwd').read()\n"
        r = self.instance.generate_with_reference("x", code, json.dumps({"kind": "int"}), count=1)
        self.assertEqual(r["error_code"], "REFERENCE_ERROR")

    def test_reference_restricted_no_import(self):
        code = "import os\ndef solve(data):\n    return os.getcwd()\n"
        r = self.instance.generate_with_reference("x", code, json.dumps({"kind": "int"}), count=1)
        self.assertEqual(r["error_code"], "REFERENCE_ERROR")

    def test_invalid_input_spec_rejected(self):
        r = self.instance.generate_with_reference("x", "def solve(data):\n    return 1\n", "not json", count=1)
        self.assertEqual(r["error_code"], "INVALID_INPUT")


class TestCaseGeneratorToolTests(unittest.TestCase):
    def test_tool_has_no_network_database_or_secrets(self):
        text = TOOL_PATH.read_text()
        for forbidden in ("httpx", "requests.", "sqlite3", "OPENAI_API_KEY", "password", "subprocess", "__import__"):
            self.assertNotIn(forbidden, text)

    def test_tool_restricts_builtins(self):
        text = TOOL_PATH.read_text()
        self.assertIn("SAFE_BUILTINS", text)
        self.assertIn('"__builtins__"', text)
        self.assertNotIn('"__import__":', text)

    def test_creator_validates_source(self):
        content = creator.build_content()
        self.assertIn("class Tools:", content)
        self.assertIn("def generate_test_cases(", content)
        self.assertIn("def generate_with_reference(", content)

    def test_creator_payload(self):
        body = creator.payload("test_case_generator", "编程题测试用例生成工具", "class Tools:", 7)
        self.assertEqual(body["id"], "test_case_generator")
        self.assertIn("测试用例", body["meta"]["description"])


if __name__ == "__main__":
    unittest.main()

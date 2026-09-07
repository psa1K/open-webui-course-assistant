import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_system_evaluation.py"
CONFIG = ROOT / "configs/system-evaluation/test-cases.json"


def load_module():
    spec = importlib.util.spec_from_file_location("verify_system_evaluation", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


evaluation = load_module()


class SystemEvaluationConfigurationTests(unittest.TestCase):
    def test_fixed_cases_cover_issue_categories(self):
        data = json.loads(CONFIG.read_text(encoding="utf-8"))
        cases = data["cases"]
        self.assertGreaterEqual(len(cases), 15)
        categories = {case["category"] for case in cases}
        self.assertTrue({"知识问答", "综合分析", "知识库无答案", "练习题生成", "练习题批改", "自定义工具调用", "错误输入/异常"}.issubset(categories))
        self.assertEqual(len({case["id"] for case in cases}), len(cases))

    def test_required_tool_cases_are_fixed(self):
        cases = {case["id"]: case for case in evaluation.read_cases()}
        self.assertEqual(cases["SYS-11"]["tool_id"], "course_practice_generator")
        self.assertEqual(cases["SYS-12"]["tool_id"], "objective_grader")
        self.assertEqual(cases["SYS-13"]["tool_id"], "course_catalog_query")
        self.assertEqual(cases["SYS-14"]["tool_id"], "knowledge_prerequisite_query")


class SystemEvaluationJudgementTests(unittest.TestCase):
    def test_no_answer_requires_explicit_refusal_without_citation(self):
        case = {"id": "SYS-09", "mode": "no_answer", "answer_terms": []}
        answer = "结论：资料中未找到相关信息，无法依据当前知识库确认。"
        result = evaluation.evaluate(case, answer, [], None)
        self.assertTrue(result["passed"])
        self.assertFalse(evaluation.evaluate(case, "结论：人口为 100 万。", [], None)["passed"])

    def test_chat_requires_actual_retrieval_citation(self):
        case = {"id": "SYS-X", "mode": "chat", "required_sources": ["06-codex-cli-安装与上手.md"], "answer_terms": ["npm"]}
        answer = "npm 安装即可。\n\n资料来源：\n- 文件：06-codex-cli-安装与上手.md\n- 章节/片段：相关检索片段"
        hits = [{"file": "06-codex-cli-安装与上手.md", "score": 0.8, "snippet": "npm", "valid": True}]
        self.assertTrue(evaluation.evaluate(case, answer, hits, None)["passed"])
        self.assertFalse(evaluation.evaluate(case, answer, [], None)["passed"])

    def test_tool_contracts_have_expected_boundaries(self):
        self.assertTrue(evaluation.tool_contract_ok({"id": "SYS-11"}, {"status": "ready", "mode": "temporary_generation", "generation_request": {"count": 2, "include_answer": False}}))
        self.assertTrue(evaluation.tool_contract_ok({"id": "SYS-12"}, {"status": "ok", "graded_count": 2, "correct_count": 1}))
        self.assertTrue(evaluation.tool_contract_ok({"id": "SYS-15"}, {"status": "error", "error_code": "INVALID_INPUT"}))
        self.assertFalse(evaluation.tool_contract_ok({"id": "SYS-15"}, {"status": "ok"}))

    def test_proposal_never_marks_change_as_approved(self):
        text = evaluation.proposal([{"test_id": "SYS-01", "passed": False, "issues_found": ["引用缺失"]}], "baseline")
        self.assertIn("OPT-01", text)
        self.assertIn("等待用户批准", text)
        self.assertNotIn("已批准", text)

    def test_safe_redacts_sensitive_fields(self):
        value = evaluation.safe({"token": "secret", "ordinary": "safe"})
        self.assertEqual(value["token"], "[REDACTED]")
        self.assertEqual(value["ordinary"], "safe")


if __name__ == "__main__":
    unittest.main()

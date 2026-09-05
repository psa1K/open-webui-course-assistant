import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools/objective_grader.py"
SCRIPT_PATH = ROOT / "scripts/create_objective_grader_tool.py"
BANK_PATH = ROOT / "data/question-bank.json"
COURSE_DIR = {"codex": "knowledge/codex-course", "math-modeling": "knowledge/math-modeling"}


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_embedded_tool():
    """Load the tool with the question bank inlined, as the installer does."""
    creator = load(SCRIPT_PATH, f"create_objective_grader_tool_{id(object())}")
    content = creator.build_content()
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
        fh.write(content)
        tmp = Path(fh.name)
    try:
        return load(tmp, f"objective_grader_{id(object())}")
    finally:
        tmp.unlink()


tool = load_embedded_tool()
creator = load(SCRIPT_PATH, "create_objective_grader_tool")
bank_data = json.loads(BANK_PATH.read_text())


def choice_questions():
    return {q["id"]: q for q in bank_data["questions"] if "options" in q and "answer_index" in q}


class ObjectiveGraderBankTests(unittest.TestCase):
    def setUp(self):
        self.instance = tool.Tools()

    def test_grade_known_correct_choice(self):
        q = next(iter(choice_questions().values()))
        letter = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[q["answer_index"]]
        result = self.instance.grade_from_bank(json.dumps({q["id"]: letter}, ensure_ascii=False))
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["graded_count"], 1)
        self.assertEqual(result["correct_count"], 1)
        self.assertEqual(result["percentage"], 100.0)

    def test_grade_known_wrong_choice(self):
        q = next(iter(choice_questions().values()))
        wrong_letter = "A" if q["answer_index"] != 0 else "B"
        result = self.instance.grade_from_bank(json.dumps({q["id"]: wrong_letter}, ensure_ascii=False))
        self.assertEqual(result["correct_count"], 0)
        self.assertEqual(result["earned_points"], 0.0)

    def test_accepts_option_text_as_answer(self):
        q = next(iter(choice_questions().values()))
        result = self.instance.grade_from_bank(json.dumps({q["id"]: q["options"][q["answer_index"]]}, ensure_ascii=False))
        self.assertEqual(result["correct_count"], 1)

    def test_accepts_1_based_number_as_answer(self):
        q = next(iter(choice_questions().values()))
        result = self.instance.grade_from_bank(json.dumps({q["id"]: str(q["answer_index"] + 1)}, ensure_ascii=False))
        self.assertEqual(result["correct_count"], 1)

    def test_unrecognized_answer_marked_wrong_not_crash(self):
        q = next(iter(choice_questions().values()))
        result = self.instance.grade_from_bank(json.dumps({q["id"]: "????"}, ensure_ascii=False))
        self.assertEqual(result["correct_count"], 0)
        self.assertEqual(result["items"][0]["student_answer_normalized"], "未识别")

    def test_non_objective_question_skipped(self):
        non_obj = [q for q in bank_data["questions"] if "options" not in q][0]
        result = self.instance.grade_from_bank(json.dumps({non_obj["id"]: "any"}, ensure_ascii=False))
        self.assertEqual(result["graded_count"], 0)
        self.assertEqual(result["skipped"][0]["reason"], "NOT_OBJECTIVE")

    def test_unknown_id_skipped(self):
        result = self.instance.grade_from_bank(json.dumps({"XX-999": "A"}, ensure_ascii=False))
        self.assertEqual(result["skipped"][0]["reason"], "UNKNOWN_QUESTION_ID")

    def test_invalid_sheet_rejected(self):
        for bad in ("not json", "[1,2,3]", "", "{}"):
            self.assertEqual(self.instance.grade_from_bank(bad)["error_code"], "INVALID_INPUT")

    def test_explanation_off_by_default_option(self):
        q = next(iter(choice_questions().values()))
        result = self.instance.grade_from_bank(json.dumps({q["id"]: "A"}, ensure_ascii=False), include_explanation=False)
        self.assertNotIn("explanation", result["items"][0])
        self.assertIn("source", result["items"][0])

    def test_bank_mode_covers_all_choice_questions(self):
        ids = set(choice_questions())
        sheet = {qid: "A" for qid in ids}
        result = self.instance.grade_from_bank(json.dumps(sheet, ensure_ascii=False))
        self.assertEqual(result["graded_count"], len(ids))


class ObjectiveGraderGeneralTests(unittest.TestCase):
    def setUp(self):
        self.instance = tool.Tools()

    def items(self, list_obj):
        return self.instance.grade_answers(json.dumps(list_obj, ensure_ascii=False))

    def test_choice_by_letter(self):
        r = self.items([{"id": "q1", "type": "choice", "question": "1+1", "options": ["1", "2", "3"], "correct": "2", "student_answer": "B"}])
        self.assertTrue(r["items"][0]["correct"])

    def test_choice_by_text(self):
        r = self.items([{"id": "q2", "type": "choice", "question": "cap", "options": ["paris", "london"], "correct": "paris", "student_answer": "paris"}])
        self.assertTrue(r["items"][0]["correct"])

    def test_multi_order_insensitive(self):
        r = self.items([{"id": "q3", "type": "multi", "question": "even", "options": ["1", "2", "3", "4"], "correct": ["2", "4"], "student_answer": ["D", "B"]}])
        self.assertTrue(r["items"][0]["correct"])
        r2 = self.items([{"id": "q3", "type": "multi", "question": "even", "options": ["1", "2", "3", "4"], "correct": ["B", "D"], "student_answer": "B,D"}])
        self.assertTrue(r2["items"][0]["correct"])

    def test_multi_wrong_selection(self):
        r = self.items([{"id": "q3", "type": "multi", "question": "even", "options": ["1", "2", "3", "4"], "correct": ["2", "4"], "student_answer": ["A", "C"]}])
        self.assertFalse(r["items"][0]["correct"])

    def test_text_exact_normalized(self):
        r = self.items([{"id": "q4", "type": "text", "question": "pi[1]", "correct": ["0"], "student_answer": "0"}])
        self.assertTrue(r["items"][0]["correct"])

    def test_text_alias_match(self):
        r = self.items([{"id": "q5", "type": "text", "question": "color", "correct": ["red", "蓝色"], "student_answer": "蓝色"}])
        self.assertTrue(r["items"][0]["correct"])

    def test_text_case_and_space_insensitive(self):
        r = self.items([{"id": "q6", "type": "text", "question": "name", "correct": ["foo bar"], "student_answer": "FooBar"}])
        self.assertTrue(r["items"][0]["correct"])

    def test_weighted_points_and_threshold(self):
        r = self.items([{"id": "a", "type": "choice", "options": ["x", "y"], "correct": "x", "student_answer": "y", "points": 3},
                        {"id": "b", "type": "choice", "options": ["x", "y"], "correct": "y", "student_answer": "y", "points": 2}])
        self.assertEqual(r["total_points"], 5.0)
        self.assertEqual(r["earned_points"], 2.0)
        self.assertEqual(r["percentage"], 40.0)
        self.assertFalse(r["passed"])

    def test_unsupported_type_skipped(self):
        r = self.items([{"id": "s1", "type": "简答题", "question": "essay", "correct": "x", "student_answer": "y"}])
        self.assertEqual(r["graded_count"], 0)
        self.assertEqual(r["skipped"][0]["reason"], "UNSUPPORTED_TYPE")

    def test_missing_fields_report_incomplete(self):
        r = self.items([{"id": "bad", "type": "choice", "question": "?", "student_answer": "A"}])
        self.assertIn("error", r["items"][0])
        self.assertFalse(r["items"][0]["correct"])

    def test_invalid_items_rejected(self):
        for bad in ("not json", {}, "[]"):
            self.assertEqual(self.instance.grade_answers(bad)["error_code"], "INVALID_INPUT")


class ObjectiveGraderToolTests(unittest.TestCase):
    def test_tool_has_no_network_database_or_secrets(self):
        text = TOOL_PATH.read_text()
        for forbidden in ("httpx", "requests.", "sqlite3", "OPENAI_API_KEY", "password", "subprocess"):
            self.assertNotIn(forbidden, text)

    def test_creator_inlines_bank_into_content(self):
        content = creator.build_content()
        self.assertIn("class Tools:", content)
        self.assertIn("def grade_from_bank(", content)
        self.assertNotIn("PLACEHOLDER_QUESTION_BANK", content)
        self.assertIn("CX-001", content)
        self.assertIn("MM-001", content)

    def test_creator_payload(self):
        body = creator.payload("objective_grader", "客观题自动判分工具", "class Tools:", len(bank_data["questions"]))
        self.assertEqual(body["id"], "objective_grader")
        self.assertEqual(body["name"], "客观题自动判分工具")
        self.assertIn("客观题自动判分", body["meta"]["description"])

    def test_bank_sources_exist(self):
        for q in bank_data["questions"]:
            path = ROOT / COURSE_DIR[q["course"]] / q["source"]["file"]
            self.assertTrue(path.exists(), f"题库来源不存在: {path}")


if __name__ == "__main__":
    unittest.main()
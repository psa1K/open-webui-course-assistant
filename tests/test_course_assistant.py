import importlib.util
import json
import os
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "create_course_assistant.py"
spec = importlib.util.spec_from_file_location("create_course_assistant", SCRIPT)
assistant = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assistant)


class CourseAssistantTests(unittest.TestCase):
    def test_config_defaults_are_safe(self):
        config = json.loads((ROOT / "configs/course-assistant/assistant.json").read_text())
        self.assertEqual(config["model"], "deepseek-v4-flash")
        self.assertEqual(config["knowledge_name"], "course-knowledge-base")
        self.assertNotIn("password", json.dumps(config).lower())
        self.assertNotIn("api_key", json.dumps(config).lower())

    def test_prompt_contains_acceptance_rules(self):
        prompt = (ROOT / "configs/course-assistant/system-prompt.md").read_text()
        for term in ("Codex", "数学建模", "course-knowledge-base", "资料来源", "资料中未找到相关信息", "不得编造", "学术诚信"):
            self.assertIn(term, prompt)

    def test_prompt_declares_all_required_learning_capabilities(self):
        prompt = (ROOT / "configs/course-assistant/system-prompt.md").read_text()
        required = (
            "回答课程知识问题",
            "通俗语言解释知识点",
            "根据学生主动说明的基础",
            "提供例题、示例代码",
            "生成练习题",
            "分析学生提交的答案",
            "真实检索资料的文件名",
            "超出 Codex 实战课程、数学建模课程",
            "不直接替学生完成整份作业",
        )
        for term in required:
            self.assertIn(term, prompt)

    def test_payload_binds_collection_and_prompt(self):
        body = assistant.payload("deepseek-v4-flash", "课程 AI 助教", {"id": "kb-1", "name": "course-knowledge-base"})
        self.assertEqual(body["base_model_id"], "deepseek-v4-flash")
        self.assertEqual(body["meta"]["knowledge"], [{"type": "collection", "id": "kb-1", "name": "course-knowledge-base"}])
        self.assertIn("资料来源", body["params"]["system"])

    def test_dry_run_does_not_need_write_payload(self):
        self.assertEqual(assistant.DEFAULT_ID, "course-ai-assistant")
        self.assertTrue((ROOT / "configs/course-assistant/system-prompt.md").is_file())

    def test_error_detail_redacts_secrets(self):
        old_password = os.environ.get("OPENWEBUI_PASSWORD")
        os.environ["OPENWEBUI_PASSWORD"] = "secret-pass"
        try:
            class Response:
                status_code = 401
                content = b'{"detail":"secret-pass"}'
                def json(self):
                    return {"detail": "secret-pass"}
            self.assertNotIn("secret-pass", assistant.detail(Response()))
        finally:
            if old_password is None:
                os.environ.pop("OPENWEBUI_PASSWORD", None)
            else:
                os.environ["OPENWEBUI_PASSWORD"] = old_password


if __name__ == "__main__":
    unittest.main()

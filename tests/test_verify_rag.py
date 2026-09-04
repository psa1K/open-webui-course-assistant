import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify_rag.py"
spec = importlib.util.spec_from_file_location("verify_rag", SCRIPT)
verify_rag = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify_rag)


class VerifyRagUnitTests(unittest.TestCase):
    def test_normalized_similarity_higher_score_is_valid(self):
        payload = {
            "documents": [["CLI 安装使用 npm 和 @openai/codex 命令"]],
            "metadatas": [[{"name": "06-codex-cli-安装与上手.md"}]],
            "distances": [[0.82]],
        }
        hits = verify_rag.normalize_hits(payload, "CLI 安装", [["cli"], ["安装", "npm"]])
        self.assertEqual(hits[0]["score"], 0.82)
        self.assertTrue(hits[0]["threshold_passed"])
        self.assertTrue(hits[0]["valid"])

    def test_relevant_content_below_threshold_is_not_valid(self):
        payload = {
            "documents": [["CLI 安装使用 npm 和 @openai/codex 命令"]],
            "metadatas": [[{"name": "06-codex-cli-安装与上手.md"}]],
            "distances": [[0.20]],
        }
        hits = verify_rag.normalize_hits(payload, "CLI 安装", [["cli"], ["安装", "npm"]])
        self.assertTrue(hits[0]["content_relevant"])
        self.assertFalse(hits[0]["threshold_passed"])
        self.assertFalse(hits[0]["valid"])

    def test_high_score_generic_content_is_not_valid(self):
        payload = {
            "documents": [["这是 Codex 课程的一般说明。"]],
            "metadatas": [[{"name": "06-codex-cli-安装与上手.md"}]],
            "distances": [[0.90]],
        }
        hits = verify_rag.normalize_hits(payload, "CLI 安装", [["cli"], ["安装", "npm"]])
        self.assertFalse(hits[0]["content_relevant"])
        self.assertFalse(hits[0]["valid"])

    def test_fake_filename_in_refusal_body_is_not_a_citation(self):
        answer = "无法确认《不存在的课程章节.md》，资料中未找到相关信息。"
        cited, unknown = verify_rag.extract_citations(answer, {"real.md"})
        self.assertEqual(cited, [])
        self.assertEqual(unknown, [])

    def test_fake_filename_in_source_section_is_detected(self):
        answer = "无法确认。\n\n资料来源：\n- 文件：不存在的课程章节.md\n- 章节/片段：虚构章节"
        cited, unknown = verify_rag.extract_citations(answer, {"real.md"})
        self.assertEqual(cited, [])
        self.assertEqual(unknown, ["不存在的课程章节.md"])

    def test_unknown_section_for_real_file_fails_fragment_check(self):
        snippets = ["本段只介绍 Codex CLI 安装命令。"]
        self.assertFalse(verify_rag.citation_fragment_supported("第九章火星人口统计", snippets))
        self.assertTrue(verify_rag.citation_fragment_supported("相关检索片段", snippets))

    def test_no_answer_with_fabricated_population_fails(self):
        case = next(item for item in verify_rag.CASES if item["id"] == "RAG-04")
        answer = "2035 年火星城市官方人口为 120 万，但资料中未找到相关信息。"
        checks = verify_rag.evaluate(case, answer, [], set())
        self.assertTrue(checks["unsupported_fact_detected"])
        self.assertFalse(checks["passed"])

    def test_chat_request_binds_unified_knowledge(self):
        class Response:
            headers = {"content-type": "application/json"}
            is_success = True

            @staticmethod
            def json():
                return {"choices": [{"message": {"content": "answer"}}]}

        class Client:
            payload = None

            def post(self, url, headers, json):
                self.payload = json
                return Response()

        client = Client()
        verify_rag.chat(client, "http://local", {}, "model", "kb-id", "q", "system", [])
        self.assertEqual(
            client.payload["files"],
            [{"type": "collection", "id": "kb-id", "name": "course-knowledge-base"}],
        )

    def test_rag03_model_connection_chunk_is_valid(self):
        payload = {
            "documents": [["#### 接入三方模型 这里以 DeepSeek 为例。首先创建 API key，再在 CC Switch 中添加模型并启用。"]],
            "metadatas": [[{"name": "08-第三方模型接入.md"}]],
            "distances": [[0.87]],
        }
        case = next(item for item in verify_rag.CASES if item["id"] == "RAG-03")
        hits = verify_rag.normalize_hits(payload, case["retrieval_queries"][0], case["support_term_groups"][0])
        self.assertTrue(hits[0]["valid"])

    def test_rag03_git_workflow_chunk_is_valid(self):
        payload = {
            "documents": [["用 Codex 做真实项目时，先新建分支，查看 diff，运行验证，commit 后 push 到 GitHub，再创建 Pull Request 审查。"]],
            "metadatas": [[{"name": "12-核心功能-mcp-与-git-github-工作流.md"}]],
            "distances": [[0.86]],
        }
        case = next(item for item in verify_rag.CASES if item["id"] == "RAG-03")
        hits = verify_rag.normalize_hits(payload, case["retrieval_queries"][1], case["support_term_groups"][1])
        self.assertTrue(hits[0]["valid"])

    def test_rag03_prefers_required_workflow_source_over_auxiliary_pdf(self):
        case = next(item for item in verify_rag.CASES if item["id"] == "RAG-03")
        preferred = set(case["preferred_sources"])
        auxiliary = {"source": "00-协作工具-环境准备.pdf", "score": 0.90, "valid": True}
        core = {"source": "12-核心功能-mcp-与-git-github-工作流.md", "score": 0.82, "valid": True}
        self.assertGreater(
            verify_rag.preferred_hit_sort_key(core, preferred),
            verify_rag.preferred_hit_sort_key(auxiliary, preferred),
        )

    def test_rag03_requires_two_specific_citations(self):
        case = next(item for item in verify_rag.CASES if item["id"] == "RAG-03")
        hits = [
            {"source": "08-第三方模型接入.md", "snippet": "DeepSeek API key 接入三方模型", "valid": True},
            {"source": "12-核心功能-mcp-与-git-github-工作流.md", "snippet": "Codex 分支 diff commit push Pull Request", "valid": True},
        ]
        answer = """结论：先完成模型接入，再使用 Git/GitHub 分支和 PR 协作。

资料来源：
- 文件：08-第三方模型接入.md
  章节/片段：相关检索片段
- 文件：12-核心功能-mcp-与-git-github-工作流.md
  章节/片段：相关检索片段"""
        all_sources = {hit["source"] for hit in hits}
        self.assertTrue(verify_rag.evaluate(case, answer, hits, all_sources)["passed"])
        incomplete = answer.replace("- 文件：12-核心功能-mcp-与-git-github-工作流.md\n  章节/片段：相关检索片段", "")
        self.assertFalse(verify_rag.evaluate(case, incomplete, hits, all_sources)["passed"])

    def test_merge_keeps_best_hit_from_each_query(self):
        class FakeClient:
            pass

        original = verify_rag.retrieve
        calls = []

        def fake_retrieve(client, base, headers, knowledge_id, question, support_term_groups=None):
            calls.append(question)
            if "模型" in question:
                return [{
                    "source": "08-第三方模型接入.md",
                    "score": 0.80,
                    "snippet": "模型接入 API",
                    "content_relevant": True,
                    "threshold_passed": True,
                    "valid": True,
                }]
            return [{
                "source": "12-核心功能-mcp-与-git-github-工作流.md",
                "score": 0.81,
                "snippet": "GitHub 工作流",
                "content_relevant": True,
                "threshold_passed": True,
                "valid": True,
            }]

        verify_rag.retrieve = fake_retrieve
        try:
            case = next(item for item in verify_rag.CASES if item["id"] == "RAG-03")
            hits, queries = verify_rag.retrieve_case(FakeClient(), "", {}, "kb", case)
        finally:
            verify_rag.retrieve = original
        self.assertEqual(len(queries), 2)
        self.assertEqual(calls, queries)
        self.assertEqual(
            {hit["source"] for hit in hits},
            {"08-第三方模型接入.md", "12-核心功能-mcp-与-git-github-工作流.md"},
        )


if __name__ == "__main__":
    unittest.main()

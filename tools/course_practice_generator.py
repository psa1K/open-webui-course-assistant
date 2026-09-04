"""Open WebUI Workspace Tool for temporary, constraint-based practice generation."""
from __future__ import annotations

from typing import Any


class Tools:
    """Validate constraints and create a retrieval-grounded generation task.

    This tool deliberately does not contain a question bank or call a model. The
    selected course assistant retrieves evidence and performs temporary generation.
    """

    def generate_practice_questions(
        self,
        course: str | None = None,
        chapter: str = "",
        difficulty: str = "medium",
        count: int = 3,
        question_types: list[str] | None = None,
        student_level: str | None = None,
        include_answer: bool = False,
    ) -> dict[str, Any]:
        normalized = {
            "course": course.strip().lower() if isinstance(course, str) and course.strip() else None,
            "chapter": chapter.strip() if isinstance(chapter, str) else chapter,
            "difficulty": difficulty.strip().lower() if isinstance(difficulty, str) else difficulty,
            "count": count,
            "question_types": [str(item).strip() for item in (question_types or []) if str(item).strip()],
            "student_level": student_level.strip() if isinstance(student_level, str) and student_level.strip() else None,
            "include_answer": bool(include_answer),
        }
        error = self._validate(normalized)
        if error:
            return {
                "status": "error",
                "error_code": "INVALID_INPUT",
                "message": error,
                "constraints": normalized,
            }

        return {
            "status": "ready",
            "mode": "temporary_generation",
            "generation_request": normalized,
            "instructions": {
                "knowledge_source": "course-knowledge-base",
                "use_retrieved_context_only": True,
                "do_not_invent_sources": True,
                "do_not_generate_complete_submitted_assignment": True,
                "output_format": "json_and_markdown",
                "no_evidence_response": "资料中未找到相关信息",
                "temporary_generation": True,
                "answer_policy": (
                    "只输出题目、提示、知识点和来源"
                    if not normalized["include_answer"]
                    else "仅输出标注为参考答案的思路、评分要点或简要答案，不代写完整作业"
                ),
            },
            "output_schema": self._output_schema(),
        }

    @staticmethod
    def _validate(values: dict[str, Any]) -> str | None:
        if values["course"] not in (None, "codex", "math-modeling"):
            return "course 只能是 codex 或 math-modeling。"
        if not isinstance(values["chapter"], str) or not values["chapter"]:
            return "chapter 不能为空，必须指定课程章节或知识模块。"
        if values["difficulty"] not in ("easy", "medium", "hard"):
            return "difficulty 只能是 easy、medium 或 hard。"
        if isinstance(values["count"], bool) or not isinstance(values["count"], int) or not 1 <= values["count"] <= 10:
            return "count 必须是 1 到 10 之间的整数。"
        if not isinstance(values["question_types"], list):
            return "question_types 必须是字符串列表。"
        if values["student_level"] is not None and not isinstance(values["student_level"], str):
            return "student_level 必须是字符串或 null。"
        if not isinstance(values["include_answer"], bool):
            return "include_answer 必须是布尔值。"
        return None

    @staticmethod
    def _output_schema() -> dict[str, Any]:
        return {
            "status": "ok",
            "course": "codex 或 math-modeling",
            "chapter": "实际章节",
            "difficulty": "easy、medium 或 hard",
            "requested_count": 3,
            "generated_count": 3,
            "questions": [{
                "number": 1,
                "type": "题型",
                "question": "根据实际检索资料临时生成",
                "hint": "解题提示",
                "knowledge_points": ["知识点"],
                "source": {"file": "实际命中文件名", "section": "实际章节或相关检索片段"},
            }],
            "sources": [{"file": "实际命中文件名", "section": "实际章节或相关检索片段"}],
            "answer_policy": {"include_answer": False, "note": "默认不输出完整答案"},
        }

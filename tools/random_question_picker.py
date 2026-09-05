"""Open WebUI Workspace Tool: randomly pick questions from a real question bank.

The embedded QUESTION_BANK mirrors data/question-bank.json in the repository
(same content, inlined because Workspace Tools run without filesystem access).
Every question cites its real source file in knowledge/ (issue #19).
"""
from __future__ import annotations

import json
import random
from typing import Any

QUESTION_BANK_JSON = json.dumps({"questions": []})  # PLACEHOLDER_QUESTION_BANK

COURSES = ("codex", "math-modeling")
DIFFICULTIES = ("easy", "medium", "hard")
QUESTION_TYPES = ("概念题", "简答题", "代码题", "建模题", "综合题")
MAX_COUNT = 10


class Tools:
    """Randomly sample questions from the embedded real question bank."""

    def pick_random_questions(
        self,
        course: str | None = None,
        chapter: str | None = None,
        difficulty: str | None = None,
        question_type: str | None = None,
        count: int = 3,
        include_answer: bool = False,
        seed: int | None = None,
    ) -> dict[str, Any]:
        normalized = {
            "course": course.strip().lower() if isinstance(course, str) and course.strip() else None,
            "chapter": chapter.strip() if isinstance(chapter, str) and chapter.strip() else None,
            "difficulty": difficulty.strip().lower() if isinstance(difficulty, str) and difficulty.strip() else None,
            "question_type": question_type.strip() if isinstance(question_type, str) and question_type.strip() else None,
            "count": count,
            "include_answer": bool(include_answer),
            "seed": seed,
        }
        error = self._validate(normalized)
        if error:
            return {"status": "error", "error_code": "INVALID_INPUT", "message": error, "constraints": normalized}

        bank = self._load_bank()
        pool = [
            q
            for q in bank["questions"]
            if (normalized["course"] is None or q["course"] == normalized["course"])
            and (normalized["chapter"] is None or normalized["chapter"] in q["chapter"])
            and (normalized["difficulty"] is None or q["difficulty"] == normalized["difficulty"])
            and (normalized["question_type"] is None or q["type"] == normalized["question_type"])
        ]
        if not pool:
            return {
                "status": "error",
                "error_code": "NO_MATCHING_QUESTIONS",
                "message": "题库中没有满足条件的题目，请放宽筛选条件。",
                "constraints": normalized,
                "bank_size": len(bank["questions"]),
            }

        rng = random.Random(normalized["seed"]) if normalized["seed"] is not None else random.SystemRandom()
        picked = rng.sample(pool, k=min(normalized["count"], len(pool)))

        questions = []
        for index, q in enumerate(picked, start=1):
            item = {
                "number": index,
                "id": q["id"],
                "course": q["course"],
                "chapter": q["chapter"],
                "difficulty": q["difficulty"],
                "type": q["type"],
                "question": q["question"],
                "hint": q.get("hint", ""),
                "knowledge_points": q.get("knowledge_points", []),
                "source": q["source"],
            }
            if "options" in q:
                item["options"] = q["options"]
            if normalized["include_answer"]:
                item["reference_answer"] = (
                    q["options"][q["answer_index"]]
                    if "options" in q and "answer_index" in q
                    else "参考要点：依据来源资料自行核对作答要点"
                )
            questions.append(item)

        return {
            "status": "ok",
            "mode": "random_pick_from_bank",
            "bank_size": len(bank["questions"]),
            "matched_pool_size": len(pool),
            "requested_count": normalized["count"],
            "picked_count": len(questions),
            "constraints": normalized,
            "questions": questions,
            "notes": {
                "answer_policy": (
                    "已包含标明为参考答案的内容，仅用于自检"
                    if normalized["include_answer"]
                    else "默认不含答案；如需参考答案请将 include_answer 置为 true"
                ),
                "do_not_generate_complete_submitted_assignment": True,
            },
        }

    @staticmethod
    def _validate(values: dict[str, Any]) -> str | None:
        if values["course"] is not None and values["course"] not in COURSES:
            return "course 只能是 codex、math-modeling 或不填。"
        if values["chapter"] is not None and not isinstance(values["chapter"], str):
            return "chapter 必须是字符串。"
        if values["difficulty"] is not None and values["difficulty"] not in DIFFICULTIES:
            return "difficulty 只能是 easy、medium、hard 或不填。"
        if values["question_type"] is not None and values["question_type"] not in QUESTION_TYPES:
            return "question_type 只能是 概念题/简答题/代码题/建模题/综合题 或不填。"
        if isinstance(values["count"], bool) or not isinstance(values["count"], int) or not 1 <= values["count"] <= MAX_COUNT:
            return f"count 必须是 1 到 {MAX_COUNT} 之间的整数。"
        if values["seed"] is not None and (isinstance(values["seed"], bool) or not isinstance(values["seed"], int)):
            return "seed 必须是整数或 null。"
        if not isinstance(values["include_answer"], bool):
            return "include_answer 必须是布尔值。"
        return None

    @staticmethod
    def _load_bank() -> dict[str, Any]:
        bank = json.loads(QUESTION_BANK_JSON)
        if not bank.get("questions"):
            raise ValueError("题库为空，请检查工具内容是否完整安装")
        return bank

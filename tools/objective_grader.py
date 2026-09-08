"""Open WebUI Workspace Tool: auto-grade objective (客观题) answers.

Two modes:
  - grade_from_bank: grade a student answer sheet against the embedded real
    question bank (data/question-bank.json, inlined; issue #20). Objective
    questions = those with options + answer_index (multiple choice). Other
    types (简答/代码/建模/综合) are reported as "needs manual grading".
  - grade_answers: general objective grading for caller-supplied questions
    (choice single/multi, or exact text match), independent of the bank.

Grading is real, deterministic structured logic - not prompt simulation.
"""
from __future__ import annotations

import json
import re
from typing import Any

QUESTION_BANK_JSON = json.dumps({"questions": []})  # PLACEHOLDER_QUESTION_BANK

CHOICE_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
SUPPORTED_OBJECTIVE = {"概念题", "选择题", "判断题"}
DEFAULT_THRESHOLD = 60.0


def _normalize_text(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"[，。、；：！？·,.;:!?'\"'`（）()【】\[\]{} ]", "", text)
    return text


def _normalize_letter(letter: str) -> int | None:
    letter = letter.strip().upper()
    if letter in CHOICE_LETTERS:
        return CHOICE_LETTERS.index(letter)
    match = re.fullmatch(r"第?\s*([1-9][0-9]*)\s*[选号项个]?", letter)
    if match:
        number = int(match.group(1))
        return number - 1
    return None


def _resolve_choice_index(raw: Any, options: list[str]) -> int | None:
    if isinstance(raw, int) and not isinstance(raw, bool):
        return raw
    if isinstance(raw, str):
        value = raw.strip()
        index = _normalize_letter(value)
        if index is not None and index < len(options):
            return index
        normalized = _normalize_text(value)
        for i, opt in enumerate(options):
            if _normalize_text(opt) == normalized:
                return i
    return None


def _parse_multi(raw: Any) -> list[str]:
    if isinstance(raw, list):
        return [_to_answer_letter(item) for item in raw if str(item).strip()]
    if isinstance(raw, str):
        value = raw.strip()
        if not value:
            return []
        if re.fullmatch(r"[A-Za-z,，、/ ]+", value):
            return [ch.upper() for ch in re.findall(r"[A-Za-z]", value)]
        return [part.strip() for part in re.split(r"[,，、/；;]", value) if part.strip()]
    return []


def _to_answer_letter(raw: Any) -> str:
    return str(raw).strip().upper()


def _choice_letter(index: int) -> str:
    return CHOICE_LETTERS[index] if 0 <= index < len(CHOICE_LETTERS) else str(index + 1)


class Tools:
    """Auto-grade objective questions with real structured logic."""

    def grade_from_bank(
        self,
        answer_sheet: str,
        include_explanation: bool = True,
    ) -> dict[str, Any]:
        sheet = self._parse_sheet(answer_sheet)
        if sheet is None:
            return {"status": "error", "error_code": "INVALID_INPUT", "message": "answer_sheet 必须是非空 JSON 对象，键为题号、值为学生答案。"}
        bank = self._load_bank()
        by_id = {q["id"]: q for q in bank["questions"]}
        results = []
        earned = 0.0
        total = 0.0
        skipped = []
        for qid, student in sheet.items():
            question = by_id.get(qid)
            if question is None:
                skipped.append({"id": qid, "reason": "UNKNOWN_QUESTION_ID"})
                continue
            if "options" not in question or "answer_index" not in question:
                skipped.append({"id": qid, "reason": "NOT_OBJECTIVE", "type": question.get("type")})
                continue
            options = question["options"]
            correct_index = int(question["answer_index"])
            student_index = _resolve_choice_index(student, options)
            if student_index is None:
                result = self._result_entry(question, 0.0, 1.0, student, correct_index, options, None, include_explanation)
            else:
                correct = student_index == correct_index
                result = self._result_entry(question, 1.0 if correct else 0.0, 1.0, student, correct_index, options, student_index, include_explanation)
            results.append(result)
            total += 1.0
            earned += result["earned_points"]
        return self._summary(results, earned, total, skipped, 0)

    def grade_answers(
        self,
        items: str,
        pass_threshold: float = DEFAULT_THRESHOLD,
        include_explanation: bool = True,
    ) -> dict[str, Any]:
        data = self._parse_items(items)
        if data is None:
            return {"status": "error", "error_code": "INVALID_INPUT", "message": "items 必须是非空 JSON 数组，每项含 type/question/student_answer 与正确值。"}
        results = []
        earned = 0.0
        total = 0.0
        skipped = []
        for idx, item in enumerate(data, start=1):
            item["number"] = int(idx)
            qtype = str(item.get("type", "")).strip()
            points = float(item.get("points", 1.0))
            if points < 0:
                points = 1.0
            if qtype in ("choice", "概念题", "选择题"):
                entry, correct = self._grade_choice(item, points, include_explanation)
            elif qtype == "multi":
                entry, correct = self._grade_multi(item, points, include_explanation)
            elif qtype in ("text", "填空题", "判断题"):
                entry, correct = self._grade_text(item, points, include_explanation)
            else:
                skipped.append({"number": idx, "id": item.get("id"), "reason": "UNSUPPORTED_TYPE", "type": qtype})
                continue
            results.append(entry)
            total += points
            earned += points if correct else 0.0
        return self._summary(results, earned, total, skipped, pass_threshold)

    def _grade_choice(self, item: dict[str, Any], points: float, include_explanation: bool) -> tuple[dict[str, Any], bool]:
        options = [str(o) for o in item.get("options", [])]
        student = item.get("student_answer")
        correct = item.get("correct") or item.get("answer")
        if not options or correct is None:
            return self._incomplete_entry(item, "choice 需要 options 与 correct"), False
        correct_index = _resolve_choice_index(correct, options)
        if correct_index is None:
            return self._incomplete_entry(item, "correct 无法对应到 options 中的选项"), False
        student_index = _resolve_choice_index(student, options)
        ok = student_index is not None and student_index == correct_index
        entry = self._entry(item, points, ok, student, correct_index, options, student_index, include_explanation)
        return entry, ok

    def _grade_multi(self, item: dict[str, Any], points: float, include_explanation: bool) -> tuple[dict[str, Any], bool]:
        options = [str(o) for o in item.get("options", [])]
        student = item.get("student_answer")
        correct = item.get("correct") or item.get("answer")
        if not options or not correct:
            return self._incomplete_entry(item, "multi 需要 options 与 correct"), False
        correct_indexes = {_resolve_choice_index(c, options) for c in (correct if isinstance(correct, list) else [correct])}
        correct_indexes.discard(None)
        student_indexes = set()
        for raw in _parse_multi(student):
            index = _resolve_choice_index(raw, options)
            if index is not None:
                student_indexes.add(index)
        ok = bool(correct_indexes) and student_indexes == correct_indexes
        entry = self._entry_multi(item, points, ok, student, options, student_indexes, include_explanation)
        return entry, ok

    def _grade_text(self, item: dict[str, Any], points: float, include_explanation: bool) -> tuple[dict[str, Any], bool]:
        student = str(item.get("student_answer", ""))
        correct = item.get("correct") or item.get("answer")
        if correct is None:
            return self._incomplete_entry(item, "text 需要 correct"), False
        accepted = [correct] if isinstance(correct, str) else list(correct)
        accepted_norm = [_normalize_text(str(a)) for a in accepted if str(a).strip()]
        ok = bool(accepted_norm) and _normalize_text(student) in accepted_norm
        entry = {
            "number": int(item.get("number", 1)),
            "id": item.get("id", ""),
            "type": item.get("type", "text"),
            "question": item.get("question", ""),
            "student_answer": student,
            "student_answer_normalized": _normalize_text(student),
            "standard_answer": " / ".join(str(a) for a in accepted),
            "correct": ok,
            "points": points,
            "earned_points": points if ok else 0.0,
        }
        if include_explanation:
            entry["explanation"] = item.get("explanation", "填空题/判断题按规范化精确匹配判分。")
        return entry, ok

    def _incomplete_entry(self, item: dict[str, Any], reason: str) -> dict[str, Any]:
        return {
            "number": int(item.get("number", 1)),
            "id": item.get("id", ""),
            "type": item.get("type", ""),
            "question": item.get("question", ""),
            "student_answer": item.get("student_answer", ""),
            "correct": False,
            "points": float(item.get("points", 1.0)),
            "earned_points": 0.0,
            "error": reason,
        }

    def _entry(self, item: dict[str, Any], points: float, ok: bool, student: Any, correct_index: int, options: list[str], student_index: int | None, include_explanation: bool) -> dict[str, Any]:
        return self._entry_multi(item, points, ok, student, options, {student_index} if student_index is not None else set(), include_explanation)

    def _entry_multi(self, item: dict[str, Any], points: float, ok: bool, student: Any, options: list[str], student_indexes: set[int], include_explanation: bool) -> dict[str, Any]:
        entry = {
            "number": int(item.get("number", 1)),
            "id": item.get("id", ""),
            "type": item.get("type", "choice"),
            "question": item.get("question", ""),
            "student_answer": str(student),
            "student_answer_normalized": "".join(sorted(_choice_letter(i) for i in student_indexes)) if student_indexes else "未识别",
            "correct": ok,
            "points": points,
            "earned_points": points if ok else 0.0,
        }
        if include_explanation:
            entry["explanation"] = item.get("explanation", "")
        return entry

    def _result_entry(self, question: dict[str, Any], earned: float, total: float, student: Any, correct_index: int, options: list[str], student_index: int | None, include_explanation: bool) -> dict[str, Any]:
        correct = earned >= total
        entry = {
            "id": question["id"],
            "type": question.get("type", "概念题"),
            "question": question["question"],
            "student_answer": str(student),
            "student_answer_normalized": _choice_letter(student_index) if student_index is not None else "未识别",
            "standard_answer": f"{_choice_letter(correct_index)} {options[correct_index]}",
            "correct": correct,
            "points": total,
            "earned_points": earned,
            "knowledge_points": question.get("knowledge_points", []),
            "source": question.get("source", {}),
        }
        if include_explanation:
            entry["explanation"] = question.get("hint", "")
        return entry

    def _summary(self, results: list[dict[str, Any]], earned: float, total: float, skipped: list[dict[str, Any]], threshold: float) -> dict[str, Any]:
        return {
            "status": "ok",
            "mode": "objective_grading",
            "graded_count": len(results),
            "correct_count": sum(1 for r in results if r.get("correct")),
            "total_points": total,
            "earned_points": round(earned, 4),
            "percentage": round(earned / total * 100, 2) if total else 0.0,
            "passed": (round(earned / total * 100, 2) >= threshold) if total else False,
            "skipped": skipped,
            "items": results,
            "notes": {"grading_is_deterministic": True, "subjective_types_require_manual_grading": True},
        }

    @staticmethod
    def _parse_sheet(answer_sheet: str) -> dict[str, Any] | None:
        if not isinstance(answer_sheet, str) or not answer_sheet.strip():
            return None
        try:
            data = json.loads(answer_sheet)
        except (ValueError, json.JSONDecodeError):
            return None
        return data if isinstance(data, dict) and data else None

    @staticmethod
    def _parse_items(items: str) -> list[dict[str, Any]] | None:
        if not isinstance(items, str) or not items.strip():
            return None
        try:
            data = json.loads(items)
        except (ValueError, json.JSONDecodeError):
            return None
        return data if isinstance(data, list) and data else None

    @staticmethod
    def _load_bank() -> dict[str, Any]:
        bank = json.loads(QUESTION_BANK_JSON)
        if not bank.get("questions"):
            raise ValueError("题库为空，请检查工具内容是否完整安装")
        return bank
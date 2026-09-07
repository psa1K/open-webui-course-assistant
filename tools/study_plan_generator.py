"""Open WebUI Workspace Tool: generate a structured study plan from the course catalog.

The tool validates and normalizes planning constraints. It does not contain a
fixed plan, call a model, access a database, or make network calls. Open
WebUI uses the returned plan request to let the assistant generate a plan from
the embedded structured course catalog.
"""
from __future__ import annotations

import json
from typing import Any

COURSE_CATALOG_JSON = json.dumps({"courses": []})  # PLACEHOLDER_COURSE_CATALOG
COURSES = ("codex", "math-modeling")
DURATIONS = ("day", "week")


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


class Tools:
    """Validate study-plan constraints and return a model-ready generation request."""

    def generate_study_plan(
        self,
        goal: str = "",
        duration: int = 4,
        duration_unit: str = "week",
        course: str | None = None,
        student_level: str | None = None,
        hours_per_week: float = 5,
        preferred_chapters: list[str] | None = None,
    ) -> dict[str, Any]:
        goal = _text(goal)
        duration_unit = _text(duration_unit).lower()
        course = _text(course).lower() or None
        student_level = _text(student_level) or None
        preferred_chapters = self._normalize_list(preferred_chapters)
        if not goal:
            return self._error("目标不能为空。", goal, duration, duration_unit, course, student_level, hours_per_week, preferred_chapters)
        if isinstance(duration, bool) or not isinstance(duration, int) or duration < 1 or duration > 52:
            return self._error("duration 必须是 1–52 的整数。", goal, duration, duration_unit, course, student_level, hours_per_week, preferred_chapters)
        if duration_unit not in DURATIONS:
            return self._error("duration_unit 只能是 day 或 week。", goal, duration, duration_unit, course, student_level, hours_per_week, preferred_chapters)
        if course not in (*COURSES, None):
            return self._error("course 只能是 codex、math-modeling 或不填。", goal, duration, duration_unit, course, student_level, hours_per_week, preferred_chapters)
        if isinstance(hours_per_week, bool) or not isinstance(hours_per_week, (int, float)) or hours_per_week <= 0 or hours_per_week > 168:
            return self._error("hours_per_week 必须大于 0 且不超过 168。", goal, duration, duration_unit, course, student_level, hours_per_week, preferred_chapters)
        catalog = self._load_catalog()
        selected = self._select_chapters(catalog, course, preferred_chapters)
        if preferred_chapters and not selected:
            return {
                "status": "ok",
                "mode": "study_plan_generation",
                "plan_request": self._request(goal, duration, duration_unit, course, student_level, hours_per_week, preferred_chapters),
                "catalog": {"knowledge_source": "structured course catalog", "matched_chapters": [], "use_catalog_only": True},
                "instructions": self._instructions(),
                "message": "目录中未找到指定章节，资料中未找到相关信息，无法据此生成可靠计划。",
            }
        plan = self._build_plan(
            goal, duration, duration_unit, course, student_level, hours_per_week, selected
        )
        return {
            "status": "ready",
            "mode": "study_plan_generation",
            "plan_request": self._request(goal, duration, duration_unit, course, student_level, hours_per_week, preferred_chapters),
            "catalog": {
                "knowledge_source": "structured course catalog",
                "use_catalog_only": True,
                "matched_chapters": [self._chapter_ref(c, ch) for c, ch in selected],
            },
            "study_plan": plan,
            "instructions": self._instructions(),
            "output_schema": self._output_schema(),
        }

    def _request(self, goal, duration, duration_unit, course, student_level, hours_per_week, preferred_chapters):
        return {"goal": goal, "duration": duration, "duration_unit": duration_unit, "course": course, "student_level": student_level, "hours_per_week": hours_per_week, "preferred_chapters": preferred_chapters}

    @staticmethod
    def _instructions() -> dict[str, Any]:
        return {
            "generate_from_catalog_only": True,
            "divide_the_requested_duration_into_phases": True,
            "include_chapter_sources": True,
            "adapt_to_student_level": True,
            "do_not_invent_chapters_or_sources": True,
            "output_format": "json_and_markdown",
        }

    def _build_plan(self, goal, duration, duration_unit, course, student_level, hours_per_week, selected):
        chapter_count = len(selected)
        phase_count = min(duration, chapter_count)
        total_hours = hours_per_week * duration if duration_unit == "week" else hours_per_week * duration / 7
        phases = []
        for index in range(phase_count):
            start = index * chapter_count // phase_count
            end = (index + 1) * chapter_count // phase_count
            chapter_refs = [self._chapter_ref(c, ch) for c, ch in selected[start:end]]
            chapter_plan = [
                {
                    "id": ch["id"],
                    "title": ch["title"],
                    "activities": ["学习本章节知识点", "根据知识点完成一次自测"],
                    "source": {"file": ch["source"]["file"], "section": ch["title"]},
                }
                for ch in chapter_refs
            ]
            phases.append(
                {
                    "phase": index + 1,
                    "title": f"第 {index + 1} 阶段",
                    "time_range": self._time_range(index, phase_count, duration, duration_unit),
                    "objectives": [f"围绕「{goal}」学习本阶段章节"],
                    "chapters": chapter_plan,
                    "deliverables": ["阶段学习笔记", "自测结果"],
                    "self_check": ["能用自己的话说明本阶段知识点", "能完成与本阶段相关的练习或操作"],
                }
            )
        sources = []
        seen = set()
        for c, ch in selected:
            source = ch["source"]
            key = (source["dir"], source["file"])
            if key not in seen:
                sources.append({"file": source["file"], "section": ch["title"]})
                seen.add(key)
        return {
            "status": "ok",
            "goal": goal,
            "duration": duration,
            "duration_unit": duration_unit,
            "course": course,
            "student_level": student_level,
            "total_hours": round(total_hours, 1),
            "phases": phases,
            "sources": sources,
        }

    @staticmethod
    def _time_range(index: int, phase_count: int, duration: int, duration_unit: str) -> str:
        start = index * duration // phase_count + 1
        end = (index + 1) * duration // phase_count
        label = "天" if duration_unit == "day" else "周"
        return f"第 {start} {label}" if start == end else f"第 {start}–{end} {label}"

    @staticmethod
    def _output_schema() -> dict[str, Any]:
        return {
            "status": "ok",
            "goal": "学习目标",
            "duration": 4,
            "duration_unit": "week",
            "course": "codex",
            "student_level": "基础",
            "total_hours": 20,
            "phases": [{"phase": 1, "title": "阶段标题", "time_range": "第 1 周", "objectives": [], "chapters": [{"id": "CX-01", "title": "真实目录章节", "activities": [], "source": {"file": "真实来源文件", "section": "章节或相关目录片段"}}], "deliverables": [], "self_check": []}],
            "sources": [{"file": "真实来源文件", "section": "章节或相关目录片段"}],
        }

    @staticmethod
    def _chapter_ref(course: dict[str, Any], chapter: dict[str, Any]) -> dict[str, Any]:
        return {"id": chapter["id"], "course": course["id"], "course_name": course["name"], "title": chapter["title"], "type": chapter.get("type", ""), "knowledge_points": chapter.get("knowledge_points", []), "source": dict(chapter.get("source", {}))}

    @staticmethod
    def _normalize_list(values: Any) -> list[str]:
        if values is None:
            return []
        if not isinstance(values, list):
            return []
        return [_text(v) for v in values if _text(v)]

    @staticmethod
    def _select_chapters(catalog: dict[str, Any], course: str | None, preferred: list[str]):
        selected = []
        needles = [x.lower() for x in preferred]
        for c in catalog.get("courses", []):
            if course and c["id"] != course:
                continue
            for ch in c.get("chapters", []):
                haystack = " ".join([ch.get("id", ""), ch.get("title", ""), *ch.get("keywords", []), *ch.get("knowledge_points", [])]).lower()
                if not needles or any(n in haystack for n in needles):
                    selected.append((c, ch))
        return selected

    @staticmethod
    def _load_catalog() -> dict[str, Any]:
        return json.loads(COURSE_CATALOG_JSON)

    @staticmethod
    def _error(message, goal, duration, duration_unit, course, student_level, hours_per_week, preferred_chapters):
        return {"status": "error", "error_code": "INVALID_INPUT", "message": message, "constraints": {"goal": goal, "duration": duration, "duration_unit": duration_unit, "course": course, "student_level": student_level, "hours_per_week": hours_per_week, "preferred_chapters": preferred_chapters}}

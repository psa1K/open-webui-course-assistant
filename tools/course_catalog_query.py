"""Open WebUI Workspace Tool: query the structured course catalog.

The embedded COURSE_CATALOG mirrors data/course-catalog.json in the repository
(inlined because Workspace Tools run without filesystem access). It holds the
structured chapters, knowledge points and source-file locations of both courses
(codex + math-modeling). Query by keyword or chapter, list by course.

Querying is real, deterministic structured search - not prompt simulation.
"""
from __future__ import annotations

import json
from typing import Any

COURSE_CATALOG_JSON = json.dumps({"courses": []})  # PLACEHOLDER_COURSE_CATALOG

COURSES = ("codex", "math-modeling")


def _normalize(value: str) -> str:
    return value.strip().lower()


class Tools:
    """Query chapters / knowledge points / material locations from the catalog."""

    def query_chapter(
        self,
        keyword: str,
        course: str | None = None,
    ) -> dict[str, Any]:
        keyword = keyword.strip() if isinstance(keyword, str) else ""
        if not keyword:
            return {"status": "error", "error_code": "INVALID_INPUT", "message": "keyword 不能为空。"}
        course = self._normalize_course(course)
        if course is False:
            return {"status": "error", "error_code": "INVALID_INPUT", "message": "course 只能是 codex、math-modeling 或不填。"}

        catalog = self._load_catalog()
        needle = _normalize(keyword)
        matches = []
        for c in catalog["courses"]:
            if course and c["id"] != course:
                continue
            for chapter in c["chapters"]:
                rank = self._match_rank(chapter, needle)
                if rank > 0:
                    matches.append(self._chapter_payload(c, chapter, rank))
        matches.sort(key=lambda item: item["rank"], reverse=True)
        if not matches:
            return {
                "status": "ok",
                "mode": "catalog_query",
                "query": {"keyword": keyword, "course": course},
                "matched_count": 0,
                "chapters": [],
                "message": f"目录中没有与「{keyword}」匹配的章节，请换用章节标题或知识点关键词。",
            }
        return {
            "status": "ok",
            "mode": "catalog_query",
            "query": {"keyword": keyword, "course": course},
            "matched_count": len(matches),
            "chapters": [self._drop_rank(item) for item in matches],
        }

    def list_chapters(self, course: str | None = None) -> dict[str, Any]:
        course = self._normalize_course(course)
        if course is False:
            return {"status": "error", "error_code": "INVALID_INPUT", "message": "course 只能是 codex、math-modeling 或不填。"}
        catalog = self._load_catalog()
        courses = []
        for c in catalog["courses"]:
            if course and c["id"] != course:
                continue
            chapters = [self._chapter_payload(c, ch, 0) for ch in c["chapters"]]
            chapters = [self._drop_rank(ch) for ch in chapters]
            courses.append({"id": c["id"], "name": c["name"], "chapter_count": len(chapters), "chapters": chapters})
        return {
            "status": "ok",
            "mode": "catalog_list",
            "course": course,
            "course_count": len(courses),
            "courses": courses,
        }

    def _match_rank(self, chapter: dict[str, Any], needle: str) -> int:
        title = _normalize(chapter.get("title", ""))
        if needle in title:
            return 4
        keywords = [_normalize(k) for k in chapter.get("keywords", [])]
        if any(needle in k or k in needle for k in keywords):
            return 3
        points = [_normalize(p) for p in chapter.get("knowledge_points", [])]
        if any(needle in p or p in needle for p in points):
            return 2
        sections = [_normalize(s) for s in chapter.get("sections", [])]
        if any(needle in s or s in needle for s in sections):
            return 1
        return 0

    def _chapter_payload(self, course: dict[str, Any], chapter: dict[str, Any], rank: int) -> dict[str, Any]:
        source = dict(chapter.get("source", {}))
        return {
            "id": chapter["id"],
            "course": course["id"],
            "course_name": course["name"],
            "title": chapter["title"],
            "type": chapter.get("type", ""),
            "knowledge_points": chapter.get("knowledge_points", []),
            "sections": chapter.get("sections", []),
            "source": source,
            "rank": rank,
        }

    @staticmethod
    def _drop_rank(item: dict[str, Any]) -> dict[str, Any]:
        return {k: v for k, v in item.items() if k != "rank"}

    @staticmethod
    def _normalize_course(course: str | None) -> str | None | bool:
        if course is None:
            return None
        if not isinstance(course, str) or not course.strip():
            return None
        value = course.strip().lower()
        if value in COURSES:
            return value
        return False

    @staticmethod
    def _load_catalog() -> dict[str, Any]:
        catalog = json.loads(COURSE_CATALOG_JSON)
        if not catalog.get("courses"):
            raise ValueError("课程目录为空，请检查工具内容是否完整安装")
        return catalog

from mcp.server import MCPServer

mcp = MCPServer("campus-course")

COURSES = [
    {
        "id": "CS101",
        "name": "Python 程序设计",
        "teacher": "张老师",
        "weekday": "周一",
        "time": "09:00-11:00",
        "credits": 3,
    },
    {
        "id": "AI201",
        "name": "人工智能导论",
        "teacher": "李老师",
        "weekday": "周三",
        "time": "14:00-16:00",
        "credits": 2,
    },
]


@mcp.tool()
def search_courses(keyword: str) -> list[dict]:
    """根据课程名称或教师姓名搜索课程。"""
    keyword = keyword.lower()

    return [
        course
        for course in COURSES
        if keyword in course["name"].lower()
        or keyword in course["teacher"].lower()
    ]


@mcp.tool()
def calculate_credits(course_ids: list[str]) -> dict:
    """计算所选课程的总学分。"""
    selected = [
        course for course in COURSES
        if course["id"] in course_ids
    ]

    return {
        "courses": [course["name"] for course in selected],
        "total_credits": sum(course["credits"] for course in selected),
    }


@mcp.resource("course://{course_id}")
def get_course(course_id: str) -> dict:
    """读取一门课程的详细信息。"""
    for course in COURSES:
        if course["id"] == course_id:
            return course

    raise ValueError(f"课程不存在：{course_id}")


@mcp.prompt()
def course_advisor(requirement: str) -> str:
    """生成选课顾问提示词。"""
    return (
        "你是一名大学选课顾问。"
        f"请根据学生的要求推荐课程：{requirement}。"
        "说明推荐理由，并计算总学分。"
    )


if __name__ == "__main__":
    mcp.run()
    # mcp.run(
    #     transport="streamable-http",
    #     host="0.0.0.0",
    #     port=8000,
    # )
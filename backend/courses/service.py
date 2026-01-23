from backend.courses.models import Course

# MVP: in-memory, sau này thay DB
COURSES = {}

def create_course(course_id: str, name: str, owner_id: str):
    course = Course(course_id, name, owner_id)
    COURSES[course_id] = course
    return course

def get_course(course_id: str):
    return COURSES.get(course_id)

def list_courses_by_owner(owner_id: str):
    return [c for c in COURSES.values() if c.owner_id == owner_id]

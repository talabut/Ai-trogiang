def check_course_access(user, course):
    if user["role"] == "teacher":
        return course.owner_id == user["id"]
    if user["role"] == "student":
        # MVP: cho phép tất cả SV (sau này gắn class)
        return True
    return False

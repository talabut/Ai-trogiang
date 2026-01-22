from backend.auth.roles import UserRole

def get_current_user():
    # MVP giả lập, sau này nối JWT
    return {
        "id": "demo_user",
        "role": UserRole.TEACHER
    }

from users.models import User

data = {
    "email": "staff@asmo.su",
    "first_name": "Staff",
    "last_name": "Staff",
    "password": "staff",
    "is_staff": True,
}

if __name__ == "__main__":
    email = data.pop("email")
    password = data.pop("password")
    user = User.objects.create_user(email, password, **data)

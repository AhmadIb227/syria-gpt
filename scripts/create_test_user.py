from config.database import SessionLocal
from app.core.security import get_password_hash
from app.repositories.user_repository import UserRepository


def main():
    db = SessionLocal()
    try:
        repo = UserRepository(db)
        email = "user@example.com"
        if repo.get_by_email(email):
            print("User already exists")
            return
        password_hash = get_password_hash("secret")
        user = repo.create(email=email, password_hash=password_hash)
        print(f"Created user: {user.email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()



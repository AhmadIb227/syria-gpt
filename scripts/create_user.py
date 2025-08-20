import argparse
from config.database import SessionLocal
from app.core.security import get_password_hash
from app.repositories.user_repository import UserRepository


def main():
    parser = argparse.ArgumentParser(description="Create a new user")
    parser.add_argument("--email", required=True, help="User email")
    parser.add_argument("--password", required=True, help="User password (will be hashed)")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        repo = UserRepository(db)
        if repo.get_by_email(args.email):
            print("User already exists")
            return
        password_hash = get_password_hash(args.password)
        user = repo.create(email=args.email, password_hash=password_hash)
        print(f"Created user: {user.email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()



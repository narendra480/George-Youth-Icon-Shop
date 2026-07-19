from sqlalchemy.orm import Session

from app.db.models import User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_email(self, email: str) -> User | None:
        return self.session.query(User).filter(User.email == email).first()

    def get_by_phone(self, phone: str) -> User | None:
        return self.session.query(User).filter(User.phone == phone).first()

    def get_by_id(self, user_id: int) -> User | None:
        return self.session.query(User).filter(User.id == user_id).first()

    def get_by_verification_token(self, token: str) -> User | None:
        return self.session.query(User).filter(User.verification_token == token).first()

    def get_by_password_reset_token(self, token: str) -> User | None:
        return self.session.query(User).filter(User.password_reset_token == token).first()

    def add(self, user: User) -> None:
        self.session.add(user)

    def save(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def commit(self) -> None:
        self.session.commit()

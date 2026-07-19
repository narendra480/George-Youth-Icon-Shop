from datetime import datetime

from sqlalchemy.orm import Session

from app.core.security import hash_token
from app.db.models import RefreshToken


class TokenRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, user_id: int, token: str, expires_at: datetime) -> RefreshToken:
        refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=hash_token(token),
            expires_at=expires_at,
        )
        self.session.add(refresh_token)
        self.session.commit()
        self.session.refresh(refresh_token)
        return refresh_token

    def get_valid_token(self, token: str) -> RefreshToken | None:
        token_hash = hash_token(token)
        refresh_token = (
            self.session.query(RefreshToken)
            .filter(RefreshToken.token_hash == token_hash)
            .first()
        )
        if not refresh_token:
            return None
        if refresh_token.revoked or refresh_token.expires_at < datetime.utcnow():
            return None
        return refresh_token

    def revoke(self, token: str) -> None:
        token_hash = hash_token(token)
        refresh_token = (
            self.session.query(RefreshToken)
            .filter(RefreshToken.token_hash == token_hash)
            .first()
        )
        if refresh_token:
            refresh_token.revoked = True
            self.session.add(refresh_token)
            self.session.commit()

    def cleanup_expired(self) -> None:
        self.session.query(RefreshToken).filter(RefreshToken.expires_at < datetime.utcnow()).delete()
        self.session.commit()

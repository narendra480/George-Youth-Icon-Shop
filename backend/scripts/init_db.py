from alembic import command
from alembic.config import Config

from app.db.migrations import seed_categories
from app.db.session import SessionLocal


def main() -> None:
    config = Config("alembic.ini")
    command.upgrade(config, "head")
    with SessionLocal() as db:
        seed_categories(db)


if __name__ == "__main__":
    main()

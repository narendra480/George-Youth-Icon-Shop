from datetime import datetime

from sqlalchemy import insert
from sqlalchemy.orm import Session

from app.db.models import Category


def seed_categories(db: Session) -> None:
    categories = [
        {"name": "Shoes", "slug": "shoes"},
        {"name": "Slippers", "slug": "slippers"},
        {"name": "Sandals", "slug": "sandals"},
        {"name": "Kids", "slug": "kids"},
        {"name": "Women", "slug": "women"},
        {"name": "Men", "slug": "men"},
        {"name": "Accessories", "slug": "accessories"},
    ]

    for category in categories:
        existing = db.query(Category).filter(Category.slug == category["slug"]).first()
        if existing:
            continue

        db.execute(
            insert(Category).values(
                name=category["name"],
                slug=category["slug"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        )
    db.commit()

from pydantic import BaseModel


class MetricsResponse(BaseModel):
    total_users: int
    total_products: int
    total_categories: int
    active_categories: int

    class Config:
        from_attributes = True
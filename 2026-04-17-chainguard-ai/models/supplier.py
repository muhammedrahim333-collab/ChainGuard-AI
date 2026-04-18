from __future__ import annotations

from pydantic import BaseModel, Field


class Supplier(BaseModel):
    supplier_id: str
    name: str
    product: str
    location: str
    city: str
    state: str = "Punjab"
    industry: str = "Manufacturing"
    quantity: float = 0
    unit: str = "kg"
    unit_cost_inr: float = 0
    website: str = ""
    email: str = ""
    phone: str = ""
    lead_time_days: int = 7
    latitude: float = Field(default=31.1471)
    longitude: float = Field(default=75.3412)

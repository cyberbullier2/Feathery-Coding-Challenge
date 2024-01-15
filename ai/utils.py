# Helper functions and classes

from typing import List, Optional
from pydantic.main import BaseModel


class Holding(BaseModel):
    name:Optional[str]
    cost_basis:Optional[float]

class PortfolioSummary(BaseModel):
    account_owner:Optional[str]
    portfolio_value:Optional[float]
    holdings: List[Holding]

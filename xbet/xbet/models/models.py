from pydantic import BaseModel


class OutcomeItem(BaseModel):
    active: bool
    odd: float
    type: str


class MarketItem(BaseModel):
    title: str
    outcomes: list[OutcomeItem]


class EventItem(BaseModel):
    id: str
    away: str
    home: str
    currentScore: str
    markets: list[MarketItem]

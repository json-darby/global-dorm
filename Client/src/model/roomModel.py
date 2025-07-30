from pydantic import BaseModel as parse_json  # no default feature for deserialisation in python?
from typing import List


class Location(parse_json):
    city: str
    county: str
    postcode: str


class Details(parse_json):
    furnished: bool
    amenities: List[str]
    live_in_landlord: bool
    shared_with: int
    bills_included: bool
    bathroom_shared: bool


class DormRoom(parse_json):
    id: int
    name: str
    location: Location
    details: Details
    price_per_month_gbp: int
    availability_date: str
    spoken_languages: List[str]
    is_available: bool


class Response(parse_json):
    status: str
    data: List[DormRoom]

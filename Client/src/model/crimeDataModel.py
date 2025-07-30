from pydantic import BaseModel as parse_json
from typing import Optional


class Street(parse_json):
    id: int
    name: str


class Location(parse_json):
    latitude: str
    longitude: str
    street: Street


class CrimeRecord(parse_json):
    category: str
    location: Location
    context: Optional[str]
    id: int
    month: str

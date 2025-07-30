# models.py
from pydantic import BaseModel as parse_json


class WeatherData(parse_json):
    date: str
    weather: str
    temp_min: int
    temp_max: int
    
import random
from pydantic import BaseModel
from typing import List, Optional


class Leg(BaseModel):
    steps: List[str]
    summary: Optional[str]
    weight: float
    duration: float
    distance: float


class Route(BaseModel):
    weight_name: str
    weight: float
    duration: float
    distance: float
    legs: List[Leg]


class Waypoint(BaseModel):
    hint: str
    distance: float
    name: Optional[str]
    location: List[float]


class OSRMResponse(BaseModel):
    code: str
    routes: List[Route]
    waypoints: List[Waypoint]

 
travel_messages = ["Have a great journey!", "Enjoy the ride!", "Wishing you a smooth trip!", "Bon voyage!", "Take care and travel well!"]
friendly_message = random.choice(travel_messages)


def generateRouteMessage(sourcePostcode, targetPostcode, duration, distance, waypoints):
    source_name = waypoints[0].name if waypoints and waypoints[0].name else "your starting point"
    target_name = waypoints[1].name if waypoints and len(waypoints) > 1 and waypoints[1].name else "your destination"

    return (f"Route from {sourcePostcode.upper()} ({source_name}) to {targetPostcode.upper()} ({target_name}):\n"
            f"It will take about {duration / 60:.2f} minutes to travel a distance of {distance / 1600:.2f} miles.\n"
            f"{friendly_message}")


'''
{
  "code": "Ok",
  "routes": [
    {
      "weight_name": "routability",
      "weight": 5795.2,
      "duration": 2518.5,
      "distance": 37223.3,
      "legs": [
        {
          "steps": [],
          "summary": "",
          "weight": 5795.2,
          "duration": 2518.5,
          "distance": 37223.3
        }
      ]
    }
  ],
  "waypoints": [
    {
      "hint": "eWfchYt5t4YNAAAABAAAAAAAAABvAAAA7T4YQbwRGkAAAAAAnwmXQg0AAAAEAAAAAAAAAG8AAAAqDQEAeRXu_x1fKwPrFO7_jF4rAwAAzxK9ZxkJ",
      "distance": 18.723123259,
      "name": "Sandringham Road",
      "location": [-1.174151, 53.174045]
    },
    {
      "hint": "Vg2UhlsNlIYYAAAAJQAAAGYAAAD1AAAAT34iQYR1d0H2BSpCKYLNQhgAAAAlAAAAZgAAAPUAAAAqDQEAufHt__tdJwNS8u3_FF4nAwMAjxW9ZxkJ",
      "distance": 10.659264116,
      "name": "",
      "location": [-1.183303, 52.911611]
    }
  ]
}
'''
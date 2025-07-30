from pydantic import BaseModel as parse_json  # no default feature for deserialisation in python
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


class Weather(parse_json):
    weather: str
    temp_min: int
    temp_max: int
    date: str


class DormRoom(parse_json):
    id: int
    name: str
    location: Location
    details: Details
    price_per_month_gbp: int
    availability_date: str
    spoken_languages: List[str]
    is_available: bool
    current_weather: Weather

    def display_room_details_left(self):
        amenities = ", ".join(self.details.amenities)
        languages = ", ".join(self.spoken_languages)
        availability = "Available" if self.is_available else "Not Available"
        landlord_status = "Yes" if self.details.live_in_landlord else "No"
        bills_status = "Included" if self.details.bills_included else "Not Included"
        bathroom_status = "Shared" if self.details.bathroom_shared else "Private"

#        # retains all formatting - '''
#        return f"""
#        Room Name: {self.name}
#        Location: {self.location.city}, {self.location.county} ({self.location.postcode})
#        Price per Month: \u00A3{self.price_per_month_gbp}
#        Availability Date: {self.availability_date}
#        Availability Status: {availability}
#
#        Room Details:
#        - Furnished: {"Yes" if self.details.furnished else "No"}
#        - Amenities: {amenities}
#        - Live-in Landlord: {landlord_status}
#        - Shared with: {self.details.shared_with} people
#        - Bills: {bills_status}
#        - Bathroom: {bathroom_status}
#
#        Spoken Languages: {languages}
#
#        Current Weather:
#        - Weather: {self.current_weather.weather}
#        - Minimum Temperature: {self.current_weather.temp_min}\u00b0C
#        - Maximum Temperature: {self.current_weather.temp_max}\u00b0C
#        - Date: {self.current_weather.date}
#        """

        result = ""
        result += "Room Name: " + self.name + "\n"
        result += "Location: " + self.location.city + ", " + self.location.county + " (" + self.location.postcode + ")\n"
        result += "Price per Month: \u00A3" + str(self.price_per_month_gbp) + "\n"
        result += "Availability Date: " + str(self.availability_date) + "\n"
        result += "Availability Status: " + availability + "\n\n"

        result += "Room Details:\n"
        result += "- Furnished: " + ("Yes" if self.details.furnished else "No") + "\n"
        result += "- Amenities: " + amenities + "\n"
        result += "- Live-in Landlord: " + landlord_status + "\n"
        if self.details.shared_with == 1:
            result += "- Shared with: " + str(self.details.shared_with) + " person\n"
        else:
            result += "- Shared with: " + str(self.details.shared_with) + " people\n"
        result += "- Bills: " + bills_status + "\n"
        result += "- Bathroom: " + bathroom_status + "\n\n"

        result += "Spoken Languages: " + languages + "\n\n"

        result += "Current Weather:\n"
        result += "- Weather: " + self.current_weather.weather + "\n"
        result += "- Minimum Temperature: " + str(self.current_weather.temp_min) + "\u00b0C\n"
        result += "- Maximum Temperature: " + str(self.current_weather.temp_max) + "\u00b0C\n"
        result += "- Date: " + str(self.current_weather.date) + "\n"
        
        return result


class Response(parse_json):
    status: str
#    data: List[DormRoom]
    data: DormRoom

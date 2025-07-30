import json
import datetime
import requests
from pydantic import ValidationError
from model.verifyUserResponseModel import VerifyUserResponse
import model.weatherModel as weatherModel
import model.roomModel as roomModel
import model.combinedRoomModel as combinedRoomModel
import model.applicationHistoryModel as applicationHistoryModel
import model.crimeDataModel as crimeDataModel
import model.routeDistanceModel as routeDistanceModel


def getData(url, postcode=""):  # API
    """Retrieves data from a given URL, optionally with a postcode, and handles API errors."""
    try:
        response = requests.get(url + postcode)
        response.raise_for_status()

        jsonData = response.json()

        if not jsonData:
            print("No data available.")
            return None

        prettyPrintJson = json.dumps(jsonData, indent=4)
        # print(prettyPrintJson)

        return prettyPrintJson, jsonData

    except requests.exceptions.Timeout:
        print("Connection timed out: Unable to connect to the server.")
    except requests.exceptions.ConnectionError:
        print("Connection failed: Server is not running.")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


def httpJson(title, url):
    """Fetches JSON data from a URL and prints it in a readable format, handling connection errors."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        prettyPrintJson = json.dumps(response.json(), indent=4)
        # print(title + ": " + pretty_print_json)
        print(f"{title}: {prettyPrintJson}")
    except requests.exceptions.Timeout:
        print("Connection timed out: Unable to connect to the server???")
    except requests.exceptions.ConnectionError:
        print("Connection failed: Server is not running.")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")


# deserialised version
def httpJsonWeatherData(url, postcode):
    """Fetches and deserialises weather data, then formats it into a string."""
    result = getData(url, postcode)

    if result is None:
        return "Failed to retrieve weather data."

    _, jsonData = result

    try:
        weather_entries = [weatherModel.WeatherData(**entry) for entry in jsonData]

        today_weather = weather_entries[0]
        tomorrow_weather = weather_entries[1]

        return (
            f"Today's Weather: {today_weather.weather} - with highs of {today_weather.temp_max}\u00b0C "
            f"and lows of {today_weather.temp_min}\u00b0C.\n"
            f"Tomorrow's Weather: {tomorrow_weather.weather} - expect highs of {tomorrow_weather.temp_max}\u00b0C "
            f"and lows of {tomorrow_weather.temp_min}\u00b0C."
        )
    except Exception as e:
        return f"Error processing weather data: {e}"


# deserialised version
def httpJsonCrimeData(url: str, postcode: str):
    """Fetches and deserialises crime data for a postcode, then provides a risk assessment and categories."""
    result = getData(url, postcode)

    if result is None:
        return None

    _, jsonData = result

    try:
        crimeRecords = [crimeDataModel.CrimeRecord(**crime) for crime in jsonData]
    except Exception as e:
        print(f"Error deserialising crime data: {e}")  #
        return None

    crimeCount = 0
    crimeCategories = {}

    for crime in crimeRecords:
        category = crime.category
        crimeCount += 1
        crimeCategories[category] = crimeCategories.get(category, 0) + 1

    if crimeCount < 50:
        dangerMessage = "Low crime risk in the area."
    elif crimeCount < 150:
        dangerMessage = "Moderate crime risk."
    elif crimeCount < 300:
        dangerMessage = "High crime risk."
    elif crimeCount < 500:
        dangerMessage = "Very high crime risk."
    else:
        dangerMessage = "Extremely high crime risk."

    return dangerMessage, crimeCategories


# deserialised version
def httpJsonDistanceData(url, sourcePostcode, targetPostcode):
    """Fetches and deserialises route distance data between two postcodes, returning formatted travel information."""
    distance_url = f"{url}startPostcode={sourcePostcode}&endPostcode={targetPostcode}"
    result = getData(distance_url)

    if result is None:
        return "Error: No data received from the server."

    _, jsonData = result

    try:
        response_data = routeDistanceModel.OSRMResponse(**jsonData)

        if not response_data.routes:
            return "Error: No routes found in the response."

        route = response_data.routes[0]
        duration = route.duration
        distance = route.distance

        return routeDistanceModel.generateRouteMessage(sourcePostcode, targetPostcode, duration, distance, response_data.waypoints)

    except ValidationError as e:
        return f"Error: Validation error while parsing the response - {e}"
    except KeyError as e:
        return f"Error: Missing key {e} in the response data."


def register_user(url, username, password, confirmPassword, timeout=10):
    """
    Registers a new user by sending their details to the database API.
    Handles password mismatch and API response statuses.
    """
    if password != confirmPassword:
        return "Error: Passwords do not match", "error"

    username_password = {"username": username, "password": password}

    try:
        response = requests.post(f"{url}/addUser", json=username_password, timeout=timeout)

        if response.status_code == 200:
            try:
                result = VerifyUserResponse(**response.json())

                if result.status == "success":
                    return f"User registered successfully: {result.message}", result.status
                else:
                    return f"Error: {result.message}", result.status
            except Exception as e:
                return f"Error in deserialisation: {str(e)}", "error"
        else:
            return f"Failed: {response.status_code} - {response.text}", "error"

    except requests.exceptions.Timeout:
        return "Offline", "error"
    except requests.exceptions.RequestException as e:
        error_code = getattr(e, 'response', None)
        return f"Error: Unable to connect. Code: {error_code.status_code if error_code else 'Unknown'}", "error"


def verify_user(url, username, password, timeout=10):
    """Verifies user credentials by querying the database API."""
    full_url = f"{url}/verifyUser?username={username}&password={password}"

    try:
        response = requests.get(full_url, timeout=timeout)

        if response.status_code == 200:
            try:
                result = VerifyUserResponse(**response.json())

                if result.status == "success":
                    return f"User verified successfully: {result.message}", result.status
                else:
                    return f"Error: {result.message}", result.status
            except Exception as e:
                return f"Error in deserialisation: {str(e)}", "error"
        else:
            return f"Failed: {response.status_code} - {response.text}", "error"

    except requests.exceptions.Timeout:
        return "Offline", "error"
    except requests.exceptions.RequestException as e:
        error_code = getattr(e, 'response', None)
        return f"Error: Unable to connect. Code: {error_code.status_code if error_code else 'Unknown'}", "error"


def fetch_dorm_room_information(database, room_name):
    """Fetches and displays detailed information for a specific dorm room from the database."""
    full_url = f"{database}/viewDormRooms?roomName={room_name}"  # one room at a time
    response = requests.get(full_url)

    if response.status_code == 200:
        response_data = roomModel.Response(**response.json())  # .json

        if response_data.data:
            room = response_data.data[0]
            return room.display_room_details_left()
        else:
            return "No room details available."
    else:
        return f"Failed to fetch data: {response.status_code}"


# marked as private, not actually private...
def _room_filter(room, min_price, max_price, city, live_in_landlord, max_roommates,
                  bills_included, shared_bathroom, languages_spoken, available_from):
    """
    Filters a single dorm room based on various criteria.
    Returns a boolean indicating if the room passes filters and an error message if any.
    """
    try:
        checks = [
            (min_price is None or float(room.price_per_month_gbp) >= float(min_price)),
            (max_price is None or float(room.price_per_month_gbp) <= float(max_price)),

            (city is None or room.location.city.lower() == city.lower()),

            (live_in_landlord == 2 or (live_in_landlord == 1 and room.details.live_in_landlord) or (live_in_landlord == 0 and not room.details.live_in_landlord)),

            (max_roommates is None or room.details.shared_with <= max_roommates),

            (bills_included == 2 or (bills_included == 1 and room.details.bills_included) or (bills_included == 0 and not room.details.bills_included)),

            (shared_bathroom == 2 or (shared_bathroom == 1 and room.details.bathroom_shared) or (shared_bathroom == 0 and not room.details.bathroom_shared)),

            (languages_spoken is None or languages_spoken.lower() in [lang.lower() for lang in room.spoken_languages]),

            (available_from is None or datetime.datetime.strptime(room.availability_date, "%Y-%m-%d") <= datetime.datetime.strptime(available_from, "%Y-%m-%d"))
        ]

        return all(checks), None

    except Exception as e:
        return False, f"Error while checking filters for room {room.name}: {e}"


def fetch_dorm_room_names(database, min_price, max_price, city, live_in_landlord, max_roommates,
                           bills_included, shared_bathroom, languages_spoken, available_from):
    """Fetches all dorm room data and filters it based on specified criteria, returning names of matching rooms."""
    full_url = f"{database}/viewAllDormRooms"

    response = requests.get(full_url)
    if response.status_code != 200:
        return [], f"Failed to fetch data: {response.status_code}"

    try:
        response_data = roomModel.Response(**response.json())
    except Exception as e:
        return [], f"Error parsing response: {e}"

    filtered_rooms = []

    for room in response_data.data:
        filter_pass, error_message = _room_filter(room, min_price, max_price, city, live_in_landlord, max_roommates,
                                                  bills_included, shared_bathroom, languages_spoken, available_from)
        if error_message:
            return [], error_message
        if filter_pass:
            filtered_rooms.append(room.name)

    if not filtered_rooms:
        return [], "No rooms available that match the filters."

    return filtered_rooms, "Rooms updated."


# this includes the weather data...
def fetch_dorm_room_combined_information(database, room_name):
    """Fetches combined dorm room information, including weather data for its location."""
    url = f"{database}/fetchDormRoomCombinedInformation?roomName={room_name}"

    response = requests.get(url)

    if response.status_code == 200:
        response_data = combinedRoomModel.Response(**response.json())
        return response_data.data.location.postcode, response_data.data.display_room_details_left()
    else:
        return "", "Error fetching room data"


def add_application(database, dorm_name, applicant_name, username, password):
    """Submits a new dorm room application to the database."""
    response = requests.post(f"{database}/addApplication", json={
        "dormName": dorm_name, "applicantName": applicant_name,
        "username": username, "password": password})

    if response.status_code == 200:
        response_data = VerifyUserResponse(**response.json())

        if response_data.status == 'success':
            return f"Application added successfully for {dorm_name} by {applicant_name}."
        else:
            return f"Error: {response_data.message}"
    else:
        return f"Failed to add application. Status code: {response.status_code}"


def cancel_application(database, username, password, dorm_name, applicant_name):
    """Sends a request to cancel a specific dorm room application."""
    cancel_application_data = {
        "username": username, "password": password,
        "dormRoomName": dorm_name, "applicantName": applicant_name}

    try:
        response = requests.patch(f"{database}/cancelApplication", json=cancel_application_data)

        if response.status_code == 200:
            response_data = VerifyUserResponse(**response.json())

            if response_data.status == 'success':
                return f"Cancellation successful for {dorm_name} by {applicant_name}."
            else:
                return f"Failed to cancel application. Status code: {response.status_code}"

    except requests.exceptions.RequestException as e:
        return f"Error making request: {e}"


def view_room_application_history(database, dorm_name):
    """Retrieves and displays the application history for a given dorm room."""
    url = f"{database}/viewRoomApplicationHistory/{dorm_name}"

    try:
        response = requests.get(url)
        response.raise_for_status()

        response_data = applicationHistoryModel.ResponseData(**response.json())

        if response_data.status == "success" and response_data.data:
            return response_data.display_rooms()
        else:
            return f"No application history for '{dorm_name}'."
    except requests.exceptions.RequestException as e:
        return f"Error fetching application history: {e}"
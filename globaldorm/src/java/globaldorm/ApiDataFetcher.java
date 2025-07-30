/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package globaldorm;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import globaldorm.model.sevenTimer.WeatherData;
import globaldorm.model.police.CrimeData;
import globaldorm.model.osrm.DirectionsResponse;
import globaldorm.model.getthedata.PostcodeCoordinates;
import globaldorm.model.openMeteo.WeatherDataAlternative;
import globaldorm.model.sevenTimer.Datasery;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.*;
import java.util.stream.Collectors;

// All deserialisation model classes were automatically generated.
// All deserialisation model classes were automatically generated.
// All deserialisation model classes were automatically generated.

/**
 * The ApiDataFetcher class is responsible for fetching various types of data
 * ...including weather, crime, and routing information.
 * It handles API requests, response parsing, and error handling,
 * and uses a Postcode API to convert coordinates (very convenient).
 *
 * @author I_NEE
 */

public class ApiDataFetcher {
    private static final String SEVENTIMER_ROOT_URL = "https://www.7timer.info/bin/civillight.php";
    private static final String SEVENTIMER_CONFIGURATION_QUERY = "&lang=en&unit=metric&output=json";
    private static final String OPENMETEO_ROOT_URL = "https://api.open-meteo.com/v1/forecast?";
    private static final String OPENMETEO_FORECAST_PARAMETERS = "&daily=weather_code,temperature_2m_max,temperature_2m_min,wind_speed_10m_max";
    private static final String POLICE_ROOT_URL = "https://data.police.uk/api/crimes-street/";
    private static final String OSRM_ROOT_URL = "https://router.project-osrm.org/route/v1/";
    private static final String API_URL = "https://api.getthedata.com/postcode/";
    public static final int SUCCESS_CODE_MIN = 200;
    public static final int SUCCESS_CODE_MAX = 226; // https://restfulapi.net/http-status-codes/
    
    private Gson gson = new Gson();

    /**
     * Fetches weather data for a given postcode using the 7Timer API.
     * If the primary API call fails, it attempts to fetch data from Open-Meteo as an alternative.
     * The method returns a simplified JSON representation of the weather forecast.
     *
     * @param postcode The postcode for which to fetch weather data.
     * @return A JSON string containing simplified weather forecast data, or an error message.
     * @throws IOException If an I/O error occurs during the API call.
     */
    public String fetchWeatherData(String postcode) throws IOException {
        String coordinatesJson = fetchCoordinates(postcode);
        PostcodeCoordinates coordinates = gson.fromJson(coordinatesJson, PostcodeCoordinates.class);

        if (coordinates != null && coordinates.getData() != null) {
            String weatherQueryParameters = "lon=" + coordinates.getData().getLongitude() + "&lat=" + coordinates.getData().getLatitude() + SEVENTIMER_CONFIGURATION_QUERY;
            HttpURLConnection urlConnection = createHttpConnection(SEVENTIMER_ROOT_URL + "?" + weatherQueryParameters);

            if (urlConnection.getResponseCode() >= SUCCESS_CODE_MIN && urlConnection.getResponseCode() <= SUCCESS_CODE_MAX) {
                String jsonResponse = readResponse(urlConnection);
                WeatherData weatherData = gson.fromJson(jsonResponse, WeatherData.class);

                List<Map<String, Object>> simplifiedWeatherData = new ArrayList<>();
                for (Datasery day : weatherData.getDataseries()) {
                    Map<String, Object> dayData = new LinkedHashMap<>();
                    String formattedDate = String.format("%d-%02d-%02d",
                            Integer.valueOf(String.valueOf(day.getDate()).substring(0, 4)),
                            Integer.valueOf(String.valueOf(day.getDate()).substring(4, 6)),
                            Integer.valueOf(String.valueOf(day.getDate()).substring(6, 8)));
                    dayData.put("date", formattedDate);
                    dayData.put("weather", day.getWeather());
                    dayData.put("temp_min", day.getTemp2M().getMin());
                    dayData.put("temp_max", day.getTemp2M().getMax());

                    simplifiedWeatherData.add(dayData);
                }
                return gson.toJson(simplifiedWeatherData);
            } else {
                return fetchWeatherDataAlternative(postcode);
            }
        } else {
            return gson.toJson(Collections.singletonMap("error", "Invalid postcode or unable to retrieve coordinates"));
        }
    }

    /**
     * Fetches alternative weather data for a given postcode using the Open-Meteo API.
     * This method is called if the primary weather data fetch (from 7Timer) fails.
     *
     * @param postcode The postcode for which to fetch alternative weather data.
     * @return A JSON string containing simplified weather forecast data from Open-Meteo, or an error message.
     * @throws IOException If an I/O error occurs during the API call.
     */
    public String fetchWeatherDataAlternative(String postcode) throws IOException {
        String coordinatesJson = fetchCoordinates(postcode);
        PostcodeCoordinates coordinates = gson.fromJson(coordinatesJson, PostcodeCoordinates.class);

        if (coordinates != null && coordinates.getData() != null) {
            String weatherQueryParameters = "latitude=" + coordinates.getData().getLatitude() + "&longitude=" + coordinates.getData().getLongitude() + OPENMETEO_FORECAST_PARAMETERS;
            HttpURLConnection urlConnection = createHttpConnection(OPENMETEO_ROOT_URL + weatherQueryParameters);

            if (urlConnection.getResponseCode() >= SUCCESS_CODE_MIN && urlConnection.getResponseCode() <= SUCCESS_CODE_MAX) {
                String jsonResponse = readResponse(urlConnection);
                WeatherDataAlternative weatherData = gson.fromJson(jsonResponse, WeatherDataAlternative.class);

                List<Map<String, Object>> simplifiedWeatherData = new ArrayList<>();
                for (int i = 0; i < weatherData.getDaily().getTime().size(); i++) {
                    Map<String, Object> dayData = new LinkedHashMap<>();
                    String formattedDate = weatherData.getDaily().getTime().get(i);
                    dayData.put("date", formattedDate);
                    dayData.put("weather", getWeatherDescription(weatherData.getDaily().getWeatherCode().get(i)));
                    dayData.put("temp_min", weatherData.getDaily().getTempMin().get(i));
                    dayData.put("temp_max", weatherData.getDaily().getTempMax().get(i));
                    simplifiedWeatherData.add(dayData);
                }
                return gson.toJson(simplifiedWeatherData);
            } else {
                return gson.toJson(Collections.singletonMap("error", "Error retrieving weather data from Open Meteo"));
            }
        } else {
            return gson.toJson(Collections.singletonMap("error", "Invalid postcode or unable to retrieve coordinates"));
        }
    }

    /**
     * Fetches crime data for a specified crime type, postcode, and optional date from the Police.uk API.
     * The fetched crime data is filtered to include only crimes within a half-mile radius of the given postcode.
     *
     * @param crime The type of crime to fetch (e.g., "all-crime", "burglary"). If {@code null} or empty, fetches all crimes.
     * @param postcode The postcode for which to fetch crime data.
     * @param date An optional date in YYYY-MM format to filter crime data.
     * @return A JSON string containing filtered crime data, or an error message.
     * @throws IOException If an I/O error occurs during the API call.
     */
    public String fetchCrimeData(String crime, String postcode, String date) throws IOException {
        String coordinatesJson = fetchCoordinates(postcode);
        PostcodeCoordinates coordinates = gson.fromJson(coordinatesJson, PostcodeCoordinates.class);

        if (coordinates != null && coordinates.getData() != null) {
            String lat = coordinates.getData().getLatitude();
            String lng = coordinates.getData().getLongitude();

            String crimeType = (crime != null && !crime.isEmpty()) ? crime : "all-crime";
            String crimeQueryParameters = "lat=" + lat + "&lng=" + lng + (date != null ? "&date=" + date : "");

            HttpURLConnection urlConnection = createHttpConnection(POLICE_ROOT_URL + crimeType + "?" + crimeQueryParameters);

            if (urlConnection.getResponseCode() >= SUCCESS_CODE_MIN && urlConnection.getResponseCode() <= SUCCESS_CODE_MAX) {
                String jsonResponse = readResponse(urlConnection);
                List<CrimeData> crimeDataList = gson.fromJson(jsonResponse, new TypeToken<List<CrimeData>>() {}.getType());

                double originLatitude = Double.parseDouble(lat);
                double originLongitude = Double.parseDouble(lng);

                List<CrimeData> filteredCrimes = crimeDataList.stream()
                        .filter(crimeData -> RadiusChecker.withinRadius(originLatitude, originLongitude,
                                Double.parseDouble(crimeData.getLocation().getLatitude()),
                                Double.parseDouble(crimeData.getLocation().getLongitude())))
                        .collect(Collectors.toList());

                return gson.toJson(filteredCrimes);
            } else {
                return gson.toJson(Collections.singletonMap("error", "Error retrieving crime data"));
            }
        } else {
            return gson.toJson(Collections.singletonMap("error", "Invalid postcode or unable to retrieve coordinates"));
        }
    }

    /**
     * Fetches route data between a starting and ending postcode using the OSRM API.
     * The route calculation is based on the specified mode of transportation.
     *
     * @param mode The mode of transportation (e.g., "car", "foot", "bike").
     * @param startPostcode The starting postcode for the route.
     * @param endPostcode The ending postcode for the route.
     * @return A JSON string containing route directions, or an error message.
     * @throws IOException If an I/O error occurs during the API call.
     */
    public String fetchRouteData(String mode, String startPostcode, String endPostcode) throws IOException {
        String startCoordinatesJson = fetchCoordinates(startPostcode);
        PostcodeCoordinates startCoordinates = gson.fromJson(startCoordinatesJson, PostcodeCoordinates.class);
        String endCoordinatesJson = fetchCoordinates(endPostcode);
        PostcodeCoordinates endCoordinates = gson.fromJson(endCoordinatesJson, PostcodeCoordinates.class);

        if (startCoordinates != null && startCoordinates.getData() != null &&
                endCoordinates != null && endCoordinates.getData() != null) {

            String startLat = startCoordinates.getData().getLatitude();
            String startLon = startCoordinates.getData().getLongitude();
            String endLat = endCoordinates.getData().getLatitude();
            String endLon = endCoordinates.getData().getLongitude();

            String routeQueryParameters = startLon + "," + startLat + ";" + endLon + "," + endLat + "?overview=false";
            HttpURLConnection urlConnection = createHttpConnection(OSRM_ROOT_URL + mode + "/" + routeQueryParameters);

            if (urlConnection.getResponseCode() >= SUCCESS_CODE_MIN && urlConnection.getResponseCode() <= SUCCESS_CODE_MAX) {
                String jsonResponse = readResponse(urlConnection);
                DirectionsResponse directionResponse = gson.fromJson(jsonResponse, new TypeToken<DirectionsResponse>() {}.getType());
                return gson.toJson(directionResponse);
            } else {
                return gson.toJson(Collections.singletonMap("error", "Error retrieving route data"));
            }
        } else {
            return gson.toJson(Collections.singletonMap("error", "Invalid postcode(s) or unable to retrieve coordinates"));
        }
    }

    /**
     * Fetches geographical coordinates (latitude and longitude) for a given postcode
     * using the "getthedata.com" postcode API.
     *
     * @param postcode The postcode for which to retrieve coordinates.
     * @return A JSON string containing the postcode coordinates, or an error message.
     * @throws IOException If an I/O error occurs during the API call.
     */
    private String fetchCoordinates(String postcode) throws IOException {
        HttpURLConnection urlConnection = createHttpConnection(API_URL + postcode);

        if (urlConnection.getResponseCode() >= SUCCESS_CODE_MIN && urlConnection.getResponseCode() <= SUCCESS_CODE_MAX) {
            return readResponse(urlConnection);
        } else {
            return gson.toJson(Collections.singletonMap("error", "Error retrieving postcode coordinates"));
        }
    }

    /**
     * Creates and configures an {@link HttpURLConnection} for a given URL string.
     * Sets the request method to GET.
     *
     * @param urlString The URL string to connect to.
     * @return An {@link HttpURLConnection} object ready for sending a GET request.
     * @throws IOException If an I/O error occurs during URL connection setup.
     */
    private HttpURLConnection createHttpConnection(String urlString) throws IOException {
        URL url = new URL(urlString);
        HttpURLConnection urlConnection = (HttpURLConnection) url.openConnection();
        urlConnection.setRequestMethod("GET");
        return urlConnection;
    }

    /**
     * Reads the entire response from an {@link HttpURLConnection}'s input stream
     * and returns it as a single string.
     *
     * @param urlConnection The {@link HttpURLConnection} from which to read the response.
     * @return A string containing the full response from the connection.
     * @throws IOException If an I/O error occurs while reading the response.
     */
    private String readResponse(HttpURLConnection urlConnection) throws IOException {
        StringBuilder response;
        try (BufferedReader in = new BufferedReader(new InputStreamReader(urlConnection.getInputStream()))) {
            String inputLine;
            response = new StringBuilder();
            while ((inputLine = in.readLine()) != null) {
                response.append(inputLine);
            }
        }
        return response.toString();
    }
    
    /**
     * Converts a the Open-Meteo weather code into a weather description like 7timer.
     *
     * @param weatherCode The integer weather code provided by the Open-Meteo API.
     * @return A string description of the weather condition.
     */
    private String getWeatherDescription(int weatherCode) {
        return switch (weatherCode) {
            case 0 -> "clear sky";
            case 1 -> "mainly clear";
            case 2 -> "partly cloudy";
            case 3 -> "cloudy";
            case 45 -> "fog";
            case 48 -> "depositing rime fog";
            case 51 -> "drizzle (light)";
            case 53 -> "drizzle (moderate)";
            case 55 -> "drizzle (dense intensity)";
            case 56 -> "freezing drizzle (light)";
            case 57 -> "freezing drizzle (dense intensity)";
            case 61 -> "rain (slight)";
            case 63 -> "rain (moderate)";
            case 65 -> "rain (heavy intensity)";
            case 66 -> "freezing rain (light)";
            case 67 -> "freezing rain (heavy intensity)";
            case 71 -> "snow fall (slight)";
            case 73 -> "snow fall (moderate)";
            case 75 -> "snow fall (heavy intensity)";
            case 77 -> "snow grains";
            case 80 -> "rain showers (slight)";
            case 81 -> "rain showers (moderate)";
            case 82 -> "rain showers (violent)";
            case 85 -> "snow showers (slight)";
            case 86 -> "snow showers (heavy)";
            case 95 -> "thunderstorm (slight)";
            case 96 -> "thunderstorm with slight hail";
            case 99 -> "thunderstorm with heavy hail";
            default -> "unknown";
        };
    }
}

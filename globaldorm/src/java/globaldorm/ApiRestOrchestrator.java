/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package globaldorm;

import java.io.IOException;
import javax.ws.rs.*;
import javax.ws.rs.core.MediaType;

/**
 * The ApiRestOrchestrator class is a RESTful API endpoint for the GlobalDorm application.
 * It exposes various endpoints to fetch data related to weather, crime, and routing
 * by sends/authorises requests to the {@link ApiDataFetcher}.
 *
 * @author I_NEE
 */
@Path("/globaldorm")
public class ApiRestOrchestrator {
    private final ApiDataFetcher apiDataFetcher = new ApiDataFetcher();

    /**
     * Fetches weather data for a given postcode.
     * This endpoint consumes a postcode and returns weather information in JSON format.
     *
     * @param postcode The postcode for which to fetch weather data.
     * @return A JSON string containing weather data or an error message if the fetch fails.
     */
    @GET
    @Path("/weather")
    @Produces(MediaType.APPLICATION_JSON)
    public String fetchWeatherData(@QueryParam("postcode") String postcode) {
        try {
            return apiDataFetcher.fetchWeatherData(postcode);
        } catch (IOException e) {
            return "{\"error\": \"Error fetching weather data\"}";
        }
    }

    /**
     * Fetches crime data for a specified crime type, postcode, and optional date.
     * If no crime type is specified, it defaults to fetching "all-crime" data.
     * The results are filtered to be within a predefined radius of the postcode.
     *
     * @param crime The type of crime to fetch (e.g., "all-crime", "burglary"). Can be {@code null} or empty for all crimes.
     * @param postcode The postcode for which to fetch crime data.
     * @param date An optional date in YYYY-MM format to filter crime data. Can be {@code null}.
     * @return A JSON string containing crime data or an error message if the fetch fails.
     */
    @GET
    @Path("/crime")
    @Produces(MediaType.APPLICATION_JSON)
    public String fetchCrimeData(@QueryParam("crime") String crime, @QueryParam("postcode") String postcode, @QueryParam("date") String date) {
        try {
            return apiDataFetcher.fetchCrimeData(crime, postcode, date);
        } catch (IOException e) {
            return "{\"error\": \"Error fetching crime data\"}";
        }
    }

    /**
     * Fetches route data between two postcodes for a specified mode of transportation.
     * This endpoint uses external routing services to calculate directions.
     *
     * @param mode The mode of transportation (just car atm).
     * @param startPostcode The starting postcode for the route.
     * @param endPostcode The ending postcode for the route.
     * @return A JSON string containing route data or an error message if the fetch fails.
     */
    @GET
    @Path("/route")
    @Produces(MediaType.APPLICATION_JSON)
    public String fetchRouteData(@QueryParam("mode") String mode, @QueryParam("startPostcode") String startPostcode, @QueryParam("endPostcode") String endPostcode) {
        try {
            return apiDataFetcher.fetchRouteData(mode, startPostcode, endPostcode);
        } catch (IOException e) {
            return "{\"error\": \"Error fetching route data\"}";
        }
    }
}

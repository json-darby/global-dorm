/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package globaldorm.database;
import globaldorm.database.deserialisation.ApplicationData;
import globaldorm.database.deserialisation.LoginDetails;
import globaldorm.database.deserialisation.CancelApplicationRequest;
import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.google.gson.JsonSyntaxException;
import java.io.IOException;
import javax.ws.rs.*;
import javax.ws.rs.core.MediaType;

// search query the rooms by price and location
// room should have weather and crime data? crime data will store the current time...
// cache - every seven days... remember the lectures...
// keep the matplotlib and display it on the other page
// also user should be able to view the rooms without logging in....

/**
 * The DatabaseOrchestrator class serves as the RESTful API endpoint for managing
 * interactions with the Dorm Room Database. It exposes various methods for viewing
 * dorm rooms, handling user authentication, and managing room applications.
 * All core database logic and operations are handled by the {@link DormDatabase} class.
 * For detailed implementation of database interactions, please refer to {@link DormDatabase}.
 *
 * @author I_NEE
 */

//http://localhost:8080/GlobalDorm/webresources/database/viewRoomApplicationHistory
// spaces = %20


// GET POST PUT PATCH DELETE
// can't overload a REST function.

@Path("/database")
public class DatabaseOrchestrator {
    private final DormDatabase dormDatabase = new DormDatabase();
    private final Gson gson = new Gson();

    @GET
    @Path("/viewAllDormRooms")
    @Produces(MediaType.APPLICATION_JSON)
    public String viewDormRooms() {
        JsonObject result = dormDatabase.viewDormRooms(null);
        return gson.toJson(result);
    }

    @GET
    @Path("/viewDormRooms")
    @Produces(MediaType.APPLICATION_JSON)
    public String viewDormRooms(@QueryParam("roomName") String roomName) {
        JsonObject result = dormDatabase.viewDormRooms(roomName);
        return gson.toJson(result);
    }

    @GET
    @Path("/fetchDormRoomCombinedInformation")
    @Produces(MediaType.APPLICATION_JSON)
    public String fetchDormRoomCombinedInformation(@QueryParam("roomName") String roomName) throws IOException {
        JsonObject result = dormDatabase.getDormRoomCombinedInformation(roomName);
        return gson.toJson(result);
    }

    @POST
    @Path("/addUser")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public String addUser(String loginDetailsJson) {
        try {
            LoginDetails loginDetails = gson.fromJson(loginDetailsJson, LoginDetails.class);

            String username = loginDetails.getUsername();
            String password = loginDetails.getPassword();

            JsonObject result = dormDatabase.addUser(username, password);
            return gson.toJson(result);
        } catch (JsonSyntaxException e) {
            JsonObject errorResponse = new JsonObject();
            errorResponse.addProperty("status", "error");
            errorResponse.addProperty("message", e.getMessage());
            return gson.toJson(errorResponse);
        }
    }

    @GET
    @Path("/verifyUser")
    @Produces(MediaType.APPLICATION_JSON)
    public String verifyUser(@QueryParam("username") String username, @QueryParam("password") String password) {
        JsonObject result = dormDatabase.verifyUser(username, password);
        return gson.toJson(result);
    }

    @POST
    @Path("/addApplication")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public String addApplication(String applicationDataJson) {
        try {
            ApplicationData applicationData = gson.fromJson(applicationDataJson, ApplicationData.class);

            String dormName = applicationData.getDormName();
            String applicantName = applicationData.getApplicantName();
            String username = applicationData.getUsername();
            String password = applicationData.getPassword();

            JsonObject result = dormDatabase.addApplications(dormName, applicantName, username, password);
            return gson.toJson(result);
        } catch (JsonSyntaxException e) {
            JsonObject errorResponse = new JsonObject();
            errorResponse.addProperty("status", "error");
            errorResponse.addProperty("message", e.getMessage());
            return gson.toJson(errorResponse);
        }
    }

    // implemented three different collections/database tables...
    @GET
    @Path("/viewRoomApplicationHistory/{dormRoomName}")
    @Produces(MediaType.APPLICATION_JSON)
    public String viewRoomApplicationHistory(@PathParam("dormRoomName") String dormRoomName) {
        JsonObject result = dormDatabase.viewRoomApplicationHistory(dormRoomName);
        return gson.toJson(result);
    }

    @PATCH // only a partial update, the application is still there...
    @Path("/cancelApplication")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public String cancelApplication(String cancelApplicationRequestJson) {
        try {
            CancelApplicationRequest cancelApplicationRequest = gson.fromJson(cancelApplicationRequestJson, CancelApplicationRequest.class);

            String username = cancelApplicationRequest.getUsername();
            String password = cancelApplicationRequest.getPassword();
            String dormRoomName = cancelApplicationRequest.getDormRoomName();
            String applicantName = cancelApplicationRequest.getApplicantName();

            JsonObject result = dormDatabase.cancelApplication(username, password, dormRoomName, applicantName);
            return gson.toJson(result);
        } catch (JsonSyntaxException e) {
            JsonObject errorResponse = new JsonObject();
            errorResponse.addProperty("status", "error");
            errorResponse.addProperty("message", e.getMessage());
            return gson.toJson(errorResponse);
        }
    }
}

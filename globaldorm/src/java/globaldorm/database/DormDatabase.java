package globaldorm.database;

import com.google.gson.*;
import com.mongodb.client.*;
import com.mongodb.client.model.Filters;
import com.mongodb.client.model.Updates;
import org.bson.Document;
import globaldorm.ApiDataFetcher;
import globaldorm.messageQueues.PushNotifications;

import java.io.FileReader;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import org.bson.BsonArray;

/**
 * The DormDatabase class manages interactions with the MongoDB database for the GlobalDorm application.
 * It handles initialisation of collections, Create, Read, Update and Delete (CRUD) operations for dorm rooms, users,
 * and applications, and integrates with external APIs for weather data. This class contains the core business logic
 * and direct database manipulation methods used by the application's orchestrators.
 *
 * @author I_NEE
 */
public class DormDatabase {
    private static final String CONNECTION_STRING = "mongodb://localhost:27017";
    private static final String DATABASE_NAME = "DormRoomDB";
    private static final String COLLECTION_NAME_DORM = "DormRooms"; // open connection to different collections
    private static final String COLLECTION_NAME_USER = "Users";
    private static final String COLLECTION_NAME_APPLICATION = "Applications";
    private static final Gson gson = new Gson();
    private static final String JSON_ROOMS_FILE_PATH = "src/java/globaldorm/database/modified_rooms.json";

    private MongoClient mongoClient;
    private MongoDatabase database;
    private final ApiDataFetcher apiDataFetcher = new  ApiDataFetcher();

    private final PushNotifications pushNotifications = new PushNotifications();


    /**
     * Initialises the 'DormRooms' collection in the MongoDB database.
     * If the collection does not exist, it creates it.
     * It then reads dorm room data from a JSON file and inserts new rooms into the collection,
     * skipping any rooms that already exist based on their ID.
     */
    public void initialiseDormCollection() {
        openConnection();

        boolean collectionExists = database.listCollectionNames().into(new ArrayList<>()).contains(COLLECTION_NAME_DORM);

        if (!collectionExists) {
            System.out.println("Collection doesn't exist, creating collection...");
            database.createCollection(COLLECTION_NAME_DORM);
        } else {
            System.out.println("Collection already exists.");
        }

        try {
            FileReader reader = new FileReader(JSON_ROOMS_FILE_PATH);
            JsonObject jsonObject = JsonParser.parseReader(reader).getAsJsonObject();
            JsonArray roomsArray = jsonObject.getAsJsonArray("rooms");

            MongoCollection<Document> collection = database.getCollection(COLLECTION_NAME_DORM);

            for (JsonElement element : roomsArray) {
                JsonObject roomObject = element.getAsJsonObject(); // each room is a json object
                Document doc = Document.parse(gson.toJson(roomObject)); // converts to "document" for MongoDB

                if (collection.find(Filters.eq("id", doc.get("id"))).first() == null) {
                    collection.insertOne(doc);
                    System.out.println("Inserted room with ID: " + doc.get("id"));
                } else {
                    System.out.println("Room with ID " + doc.get("id") + " already exists. Skipping it!");
                }
            }
        } catch (IOException e) {
            System.err.println("Error reading JSON file: " + e.getMessage());
        }
    }

    /**
     * Initialises the 'Users' collection in the MongoDB database.
     * If the collection does not exist, it creates it.
     */
    public void initialiseUserCollection() {
        openConnection();

        boolean collectionExists = database.listCollectionNames().into(new ArrayList<>()).contains(COLLECTION_NAME_USER);

        if (!collectionExists) {
            System.out.println("Users collection doesn't exist, creating collection...");
            database.createCollection(COLLECTION_NAME_USER);
        } else {
            System.out.println("Users collection already exists.");
        }
    }

    /**
     * Initialises the 'Applications' collection in the MongoDB database.
     * If the collection does not exist, it creates it.
     */
    public void initialiseApplicationCollection() {
        openConnection();
        boolean collectionExists = database.listCollectionNames().into(new ArrayList<>()).contains(COLLECTION_NAME_APPLICATION);

        if (!collectionExists) {
            System.out.println("Applications collection doesn't exist, creating collection...");
            database.createCollection(COLLECTION_NAME_APPLICATION);
        } else {
            System.out.println("Applications collection already exists.");
        }
    }

    /**
     * Calls all initialisation methods to set up the DormRooms, Applications, and Users collections.
     */
    public void initialiseAll() {
        initialiseDormCollection();
        initialiseApplicationCollection();
        initialiseUserCollection();
    }

    /**
     * Retrieves all dorm rooms from the database.
     * This is an overloaded method that calls {@link #viewDormRooms(String)} with a {@code null} room name.
     *
     * @return A {@link JsonObject} containing a success status and a JSON array of all dorm rooms, or an error message.
     */
    public JsonObject viewDormRooms() { // overload for one or many...
        return viewDormRooms(null);
    }

    /**
     * Retrieves dorm rooms from the database.
     * If a {@code roomName} is provided, it fetches details for that specific room.
     * If {@code roomName} is {@code null} or empty, it fetches details for all dorm rooms.
     *
     * @param roomName The name of the dorm room to retrieve, or {@code null} to retrieve all rooms.
     * @return A {@link JsonObject} containing a success status and a JSON array of dorm rooms, or an error message.
     */
    public JsonObject viewDormRooms(String roomName) {
        JsonObject outcome = new JsonObject();
        openConnection();

        try {
            MongoCollection<Document> dormCollection = database.getCollection(COLLECTION_NAME_DORM);
            ArrayList<Document> documents = new ArrayList<>();

            if (roomName != null && !roomName.isEmpty()) {
                dormCollection.find(Filters.eq("name", roomName)).into(documents);
            } else {
                dormCollection.find().into(documents);
            }

            JsonArray dormRoomsArray = new JsonArray();
            for (Document document : documents) {
                JsonObject dormRoom = JsonParser.parseString(document.toJson()).getAsJsonObject();
                dormRoomsArray.add(dormRoom);
            }

            outcome.addProperty("status", "success");
            outcome.add("data", dormRoomsArray);
        } catch (JsonSyntaxException e) {
            outcome.addProperty("status", "error");
            outcome.addProperty("message", "Failed to retrieve dorm rooms: " + e.getMessage());
        }
        return outcome;
    }

    /**
     * Retrieves combined information for a specific dorm room, including its details
     * and up-to-date weather data for its location. If weather data is not present
     * or is outdated, it fetches fresh data from an external API and updates the database.
     *
     * @param roomName The name of the dorm room for which to retrieve combined information.
     * @return A {@link JsonObject} containing the dorm room's combined information, including current weather, or an error message.
     * @throws IOException If an I/O error occurs during the external API call for weather data.
     */
    public JsonObject getDormRoomCombinedInformation(String roomName) throws IOException {
        JsonObject response = new JsonObject();
        openConnection();

        try {
            MongoCollection<Document> dormCollection = database.getCollection(COLLECTION_NAME_DORM);
            Document dormRoom = dormCollection.find(Filters.eq("name", roomName)).first();

            if (dormRoom == null) {
                response.addProperty("status", "error");
                response.addProperty("message", "Dorm room not found");
                return response;
            }

            JsonObject dormRoomData = JsonParser.parseString(dormRoom.toJson()).getAsJsonObject();

            SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd");
            String todayDate = dateFormat.format(new Date());

            JsonObject currentWeather = null;
            if (dormRoomData.has("weekly_weather")) {
                JsonArray weeklyWeatherData = dormRoomData.getAsJsonArray("weekly_weather");
                for (int i = 0; i < weeklyWeatherData.size(); i++) {
                    JsonObject dailyWeather = weeklyWeatherData.get(i).getAsJsonObject();
                    String weatherDate = dailyWeather.get("date").getAsString();
                    if (todayDate.equals(weatherDate)) {
                        currentWeather = dailyWeather;
                        break;
                    }
                }
            }

            if (currentWeather == null) {
                String postcode = dormRoomData.getAsJsonObject("location").get("postcode").getAsString().replaceAll("\\s+", "");
                String freshWeatherDataJson = apiDataFetcher.fetchWeatherData(postcode);

                JsonArray freshWeatherDataArray = JsonParser.parseString(freshWeatherDataJson).getAsJsonArray();
                JsonArray weeklyWeatherData = new JsonArray();

                for (int i = 0; i < freshWeatherDataArray.size(); i++) {
                    JsonObject dailyWeather = freshWeatherDataArray.get(i).getAsJsonObject();
                    JsonObject dailyWeatherData = new JsonObject();
                    dailyWeatherData.addProperty("weather", dailyWeather.get("weather").getAsString());
                    dailyWeatherData.addProperty("temp_min", dailyWeather.get("temp_min").getAsInt());
                    dailyWeatherData.addProperty("temp_max", dailyWeather.get("temp_max").getAsInt());
                    dailyWeatherData.addProperty("date", dailyWeather.get("date").getAsString());

                    weeklyWeatherData.add(dailyWeatherData);

                    if (todayDate.equals(dailyWeather.get("date").getAsString())) {
                        currentWeather = dailyWeatherData;
                    }
                }

                // subject to change
    //            dormRoomData.add("weekly_weather", weeklyWeatherData);

                // Update the document in MongoDB with the new weekly weather data
                dormCollection.updateOne(
                    Filters.eq("name", roomName),
                    Updates.set("weekly_weather", BsonArray.parse(weeklyWeatherData.toString()))
                );
            }

            // add current weather
            if (currentWeather != null) {
                dormRoomData.add("current_weather", currentWeather);
            }

            // remove the weekly data
            dormRoomData.remove("weekly_weather");

            response.addProperty("status", "success");
            response.add("data", dormRoomData);

        } catch (JsonSyntaxException e) {
            response.addProperty("status", "error");
            response.addProperty("message", "Failed to retrieve combined information: " + e.getMessage());
        }

        return response;
    }

    /**
     * Adds a new application for a dorm room to the database.
     * Before adding, it verifies the user credentials and checks if the room is available
     * and if the user has already applied for the room.
     *
     * @param dormName The name of the dorm room the user is applying for.
     * @param applicantName The name of the applicant.
     * @param username The username of the applicant.
     * @param password The password of the applicant.
     * @return A {@link JsonObject} indicating the success or failure of the application addition.
     */
    public JsonObject addApplications(String dormName, String applicantName, String username, String password) {
        JsonObject outcome = new JsonObject();
        openConnection();

        MongoCollection<Document> usersCollection = database.getCollection(COLLECTION_NAME_USER);
        Document user = usersCollection.find(Filters.and(Filters.eq("username", username), Filters.eq("password", password))).first();

        if (user == null) {
            outcome.addProperty("status", "error");
            outcome.addProperty("message", "Invalid username or password. Application not added.");
            return outcome;
        }

        MongoCollection<Document> dormCollection = database.getCollection(COLLECTION_NAME_DORM);
        Document room = dormCollection.find(Filters.eq("name", dormName)).first();

        if (room == null || !room.getBoolean("is_available", false)) {
            outcome.addProperty("status", "error");
            outcome.addProperty("message", "Room is not available for application.");
            return outcome;
        }

        MongoCollection<Document> applicationsCollection = database.getCollection(COLLECTION_NAME_APPLICATION);
        Document existingApplication = applicationsCollection.find(
            Filters.and(
                Filters.eq("dorm_name", dormName),
                Filters.eq("username", username)
            )
        ).first();

        if (existingApplication != null) {
            outcome.addProperty("status", "error");
            outcome.addProperty("message", "You have already applied for this dorm room.");
            return outcome;
        }

        String applicationDate = new SimpleDateFormat("yyyy-MM-dd").format(new Date());
        Document applicationDoc = new Document("dorm_name", dormName)
                .append("applicant_name", applicantName)
                .append("username", username)
                .append("application_date", applicationDate)
                .append("application_status", "pending");

        applicationsCollection.insertOne(applicationDoc);

        outcome.addProperty("status", "success");
        outcome.addProperty("message", "Application added for dorm: " + dormName + " by " + applicantName);
        return outcome;
    }

    /**
     * Adds a new user to the 'Users' collection in the database.
     * It checks if a user with the given username already exists before adding.
     *
     * @param username The username for the new user.
     * @param password The password for the new user.
     * @return A {@link JsonObject} indicating the success or failure of the user addition.
     */
    public JsonObject addUser(String username, String password) {
        JsonObject outcome = new JsonObject();
        openConnection();

        try {
            MongoCollection<Document> usersCollection = database.getCollection(COLLECTION_NAME_USER);

            Document existingUser = usersCollection.find(Filters.eq("username", username)).first();

            if (existingUser != null) {
                outcome.addProperty("status", "error");
                outcome.addProperty("message", "User with username " + username + " already exists.");
            } else {
                Document newUser = new Document("username", username).append("password", password);

                usersCollection.insertOne(newUser);

                outcome.addProperty("status", "success");
                outcome.addProperty("message", "User " + username + " has been successfully added.");
            }

        } catch (Exception e) {
            outcome.addProperty("status", "error");
            outcome.addProperty("message", "Failed to add user: " + e.getMessage());
        }

        return outcome;
    }

    /**
     * Verifies if a user with the provided username and password exists in the database.
     *
     * @param username The username to verify.
     * @param password The password to verify.
     * @return A {@link JsonObject} indicating the success or failure of the user verification.
     */
    public JsonObject verifyUser(String username, String password) {
        JsonObject outcome = new JsonObject();
        openConnection();

        MongoCollection<Document> usersCollection = database.getCollection(COLLECTION_NAME_USER);
        Document user = usersCollection.find(Filters.and(
            Filters.eq("username", username),
            Filters.eq("password", password)
        )).first();

        if (user != null) {
            outcome.addProperty("status", "success");
            outcome.addProperty("message", "User verified successfully.");
        } else {
            outcome.addProperty("status", "error");
            outcome.addProperty("message", "Invalid username or password.");
        }

        return outcome;
    }

    /**
     * Modifies the status of a specific application. This method is intended for internal or testing use,
     * as client applications should not have direct access to alter application statuses arbitrarily.
     * Valid statuses are "accepted", "rejected", "cancelled", and "pending".
     *
     * @param applicantName The name of the applicant whose application status is to be modified.
     * @param newStatus The new status to set for the application.
     * @return A {@link JsonObject} indicating the success or failure of the status update.
     */
    public JsonObject modifyApplicationStatus(String applicantName, String newStatus) {
        JsonObject outcome = new JsonObject();
        openConnection();

        if (!(newStatus.equals("accepted") || newStatus.equals("rejected") || newStatus.equals("cancelled") || newStatus.equals("pending"))) {
            outcome.addProperty("status", "error");
            outcome.addProperty("message", "Invalid status. Allowed values are 'accepted', 'rejected', 'cancelled', 'pending'.");
            return outcome;
        }

        MongoCollection<Document> applicationsCollection = database.getCollection(COLLECTION_NAME_APPLICATION);

        Document application = applicationsCollection.find(Filters.eq("applicant_name", applicantName)).first();

        if (application == null) {
            outcome.addProperty("status", "error");
            outcome.addProperty("message", "No application found for applicant " + applicantName);
            return outcome;
        }

        applicationsCollection.updateOne(
                Filters.eq("applicant_name", applicantName),
                Updates.set("application_status", newStatus)
        );

        outcome.addProperty("status", "success");
        outcome.addProperty("message", "Application status updated to " + newStatus);
        return outcome;
    }

    /**
     * Cancels a dorm room application.
     * It verifies the user's credentials, checks if the application exists and is not already cancelled,
     * then updates the application status to "cancelled" and sets the corresponding dorm room as available.
     *
     * @param username The username of the applicant initiating the cancellation.
     * @param password The password of the applicant initiating the cancellation.
     * @param dormRoomName The name of the dorm room associated with the application to be cancelled.
     * @param applicantName The name of the applicant whose application is being cancelled.
     * @return A {@link JsonObject} indicating the success or failure of the application cancellation.
     */
    public JsonObject cancelApplication(String username, String password, String dormRoomName, String applicantName) {
        JsonObject outcome = new JsonObject();
        openConnection();

        MongoCollection<Document> usersCollection = database.getCollection(COLLECTION_NAME_USER);
        Document user = usersCollection.find(Filters.and(
            Filters.eq("username", username),
            Filters.eq("password", password)
        )).first();

        if (user == null) {
            outcome.addProperty("status", "error");
            outcome.addProperty("message", "Invalid username or password.");
            return outcome;
        }

        MongoCollection<Document> applicationsCollection = database.getCollection(COLLECTION_NAME_APPLICATION);
        Document application = applicationsCollection.find(Filters.and(
            Filters.eq("dorm_name", dormRoomName),
            Filters.eq("applicant_name", applicantName)
        )).first();

        if (application == null) {
            outcome.addProperty("status", "error");
            outcome.addProperty("message", "No application found for the specified room and applicant.");
            return outcome;
        }

        String applicationStatus = application.getString("application_status");
        if ("cancelled".equalsIgnoreCase(applicationStatus)) {
            outcome.addProperty("status", "error");
            outcome.addProperty("message", "The application has already been cancelled. You cannot cancel it again.");
            return outcome;
        }

        applicationsCollection.updateOne(
            Filters.and(
                Filters.eq("dorm_name", dormRoomName),
                Filters.eq("applicant_name", applicantName)
            ),
            Updates.set("application_status", "cancelled")
        );

        MongoCollection<Document> dormCollection = database.getCollection(COLLECTION_NAME_DORM);
        dormCollection.updateOne(
            Filters.eq("name", dormRoomName),
            Updates.set("is_available", true)
        );

        outcome.addProperty("status", "success");
        outcome.addProperty("message", "Application for " + dormRoomName + " cancelled successfully. Room is now available.");
        return outcome;
    }

    /**
     * Retrieves the application history for a specified dorm room.
     *
     * @param dormRoomName The name of the dorm room for which to retrieve application history.
     * @return A {@link JsonObject} containing a success status and a JSON array of past applications for the room, or an error message.
     */
    public JsonObject viewRoomApplicationHistory(String dormRoomName) {
        JsonObject outcome = new JsonObject();
        openConnection();

        MongoCollection<Document> applicationsCollection = database.getCollection(COLLECTION_NAME_APPLICATION);

        ArrayList<Document> applications = new ArrayList<>();
        applicationsCollection.find(Filters.eq("dorm_name", dormRoomName)).into(applications);

        if (applications.isEmpty()) {
            outcome.addProperty("status", "error");
            outcome.addProperty("message", "No applications found for this room.");
            return outcome;
        }

        JsonArray applicationsHistoryArray = new JsonArray();
        for (Document application : applications) {
            JsonObject applicationHistory = new JsonObject();
            applicationHistory.addProperty("dorm_name", application.getString("dorm_name"));
            applicationHistory.addProperty("applicant_name", application.getString("applicant_name"));
            applicationHistory.addProperty("application_date", application.getString("application_date"));
            applicationHistory.addProperty("application_status", application.getString("application_status"));

            applicationsHistoryArray.add(applicationHistory);
        }

        outcome.addProperty("status", "success");
        outcome.add("data", applicationsHistoryArray);
        return outcome;
    }

    /**
     * Opens a connection to the MongoDB database.
     * This method ensures that a single client and database instance are used for all operations
     * to promote connection pooling and efficiency.
     */
    private void openConnection() {
        if (mongoClient == null) {
            mongoClient = MongoClients.create(CONNECTION_STRING); // Connection pooling
            database = mongoClient.getDatabase(DATABASE_NAME);
        }
    }

    /**
     * Dumps all dorm room data from the database into a prettified JSON format.
     * This method is useful for debugging or exporting the entire dataset.
     *
     * @return A {@link JsonObject} containing a success status and the prettified JSON data of all dorm rooms, or an error message.
     */
    public JsonObject dataDump() {
        JsonObject outcome = new JsonObject();
        openConnection();
        try {
            MongoCollection<Document> dormCollection = database.getCollection(COLLECTION_NAME_DORM);
            ArrayList<Document> documents = new ArrayList<>();
            dormCollection.find().into(documents);

            JsonArray jsonArray = new JsonArray();
            for (Document document : documents) {
                JsonObject jsonObject = JsonParser.parseString(document.toJson()).getAsJsonObject();
                jsonArray.add(jsonObject);
            }
            Gson gsonPretty = new GsonBuilder().setPrettyPrinting().create();
            outcome.addProperty("status", "success");
            outcome.add("data", JsonParser.parseString(gsonPretty.toJson(jsonArray)));
        } catch (JsonSyntaxException e) {
            outcome.addProperty("status", "error");
            outcome.addProperty("message", "Failed to retrieve data: " + e.getMessage());
        }
        return outcome;
    }

    /**
     * Sends a push notification message. This method delegates the actual notification
     * sending to the {@link PushNotifications} class, presumably for fanout or
     * broadcast functionality.
     *
     * @param message The message content to be sent as a push notification.
     */
    public void sendNotification(String message) {
        pushNotifications.pushNotificationFanout(message);
    }


    /**
     * Main method for testing the RabbitMQ notification system.
     * This method contains example calls for sending notifications.
     *
     * @param args Command line arguments (not used).
     * @throws IOException If an I/O error occurs during notification sending.
     * @throws InterruptedException If the thread is interrupted while sleeping.
     */
    public static void main(String[] args) throws IOException, InterruptedException {
        DormDatabase db = new DormDatabase();
//        db.initialiseAll();
//        JsonObject answer = db.getDormRoomCombinedInformation("Cozy Room in Shared House");
//        System.out.println(answer);
//        db.sendNotification("You could run this on your computer...");
//        Thread.sleep(2000);
//        db.sendNotification("and it'd appear right here...");
//        Thread.sleep(2000);

        db.sendNotification("15 rooms are currently available. Don't miss out!");
        Thread.sleep(2000);
        db.sendNotification("\"The best booking app since booking.com!\" - Anonymous Reviewer");
        Thread.sleep(2000);
        db.sendNotification("\"I found my dream room in seconds!\" - A Satisfied User");
        Thread.sleep(2000);
        db.sendNotification("Breaking News: \"Global Dorm is taking over the world... one room at a time!\"");
        Thread.sleep(2000);
        db.sendNotification("\"I was lost until I found this app. Now I have a room and a purpose.\" - Happy Customer");
        Thread.sleep(2000);
        db.sendNotification("\"This app saved me from couch surfing forever.\" - Grateful User");
        Thread.sleep(2000);
        db.sendNotification("\"Five stars! I’d recommend Global Dorm to everyone I know.\" - Room Seeker Extraordinaire");
        Thread.sleep(2000);
        db.sendNotification("New Feature Alert: Filter rooms like never before! Choose by max roommates, live-in landlord, and more. Try it now!");
        Thread.sleep(2000);
        db.sendNotification("Stay Informed: You can now view the current weather for each dorm location. Plan your day with ease!");
        Thread.sleep(2000);
        db.sendNotification("Worried about travel? You can now see estimated travel times to each dorm. Travel smarter, not harder!");
    }
}
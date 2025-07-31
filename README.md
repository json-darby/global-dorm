# Global Dorm: A Client-Server Prototype
This project is a streamlined, client-server prototype for a student accommodation platform. 
It showcases a heterogeneous Service-Oriented Architecture (SOA) by using a Python desktop client that communicates with a Java backend.

## System Outline
This diagram illustrates the flow of information and interaction between the system's core components, from the client UI to the backend services and database.

<p align="center">
  <img width="8917" height="5743" alt="Implementation Diagram" src="https://github.com/user-attachments/assets/7655b223-99a8-4334-bd9b-ffb817a5ece9"/>
</p>

### Key Features
* **Accommodation Search & Filter:** Users can efficiently search for available rooms with powerful filters for price, city, live-in landlord, and spoken languages.

* **Application Management:** A secure registration and login system allows users to apply for and manage room applications using RESTful methods (GET, POST, PATCH).

* **Integrated APIs:** The backend orchestrates several external APIs to provide essential local insights:

  * **Weather:** Uses 7timer as a primary API with Open Meteo as a backup for high Quality of Service (QoS).
  
  * **Safety:** Integrates Police.uk crime data, with a Haversine formula applied to filter results within a half-mile radius.
  
  * **Commute:** Calculates travel distance by car using the Project-OSRM API.
  
  * **Usability:** The GetTheData API allows for postcode-based location inputs, enhancing user experience.

* **Performance & Reliability:** The system includes a caching layer for weather data to reduce API calls and latency. It also features a RabbitMQ push notification system for real-time updates and a server toggle to switch between a cloud deployment and a local Docker container.

* **Robust Deserialisation:** All JSON requests and responses are deserialised for accurate error handling and clear, user-friendly messages.

## A Visual Showcase
### Home Page
<p align="center">
<img src="https://github.com/user-attachments/assets/b83bc45f-4ec1-4d12-8152-90da2d4950c6" width="80%"/>
</p>
This is the home screen where users can register for a new account or log in. The Python client uses the Java backend to securely manage user details in a MongoDB database.

### Search and Apply for Rooms
<p align="center">
<img src="https://github.com/user-attachments/assets/24b0f385-1776-4e95-bc12-4ec6dfd6a6fd" width="80%"/>  
</p>
This view shows the Search and Apply for Rooms interface, a key part of the application's functionality. Users can browse a list of rooms and view detailed descriptions. 
The interface also displays a dynamic bar chart of local crime data and offers options to calculate the commute distance from an entered postcode. 
Additionally, users can refine their search with a drop-down filter based on criteria like price, amenities, and spoken languages, and can apply for, cancel, or view the history of room applications.

---

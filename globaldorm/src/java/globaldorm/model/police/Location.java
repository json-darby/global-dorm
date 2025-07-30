/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package globaldorm.model.police;

/**
 *
 * @author I_NEE
 */

public class Location {
    private String latitude;
    private Street street;
    private String longitude;

    public String getLatitude() { return latitude; }
    public void setLatitude(String latitude) { this.latitude = latitude; }

    public Street getStreet() { return street; }
    public void setStreet(Street street) { this.street = street; }

    public String getLongitude() { return longitude; }
    public void setLongitude(String longitude) { this.longitude = longitude; }
}

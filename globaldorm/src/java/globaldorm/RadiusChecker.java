/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package globaldorm;

/**
 * The RadiusChecker class provides a utility method to determine if a target
 * geographical point is within a specified radius of an origin point.
 * It uses the Haversine formula to calculate the distance between two
 * sets of coordinates.
 * This reduces the result of the crime api data.
 *
 * @author I_NEE
 */

public class RadiusChecker {
    private static final double RADIUS_OF_EARTH = 3958.8;
    private static final double MILE_RADIUS = 0.5;
    // urban or suburban???

    public static boolean withinRadius(double originLatitude, double originLongitude, double targetLatitude, double targetLongitude) {

        double latitudeDifference = Math.toRadians(targetLatitude - originLatitude);
        double longitudeDifference = Math.toRadians(targetLongitude - originLongitude);

        // The angular distance squared #Haversine Formula
        double a = Math.sin(latitudeDifference / 2) * Math.sin(latitudeDifference / 2) +
                   Math.cos(Math.toRadians(originLatitude)) * Math.cos(Math.toRadians(targetLatitude)) *
                   Math.sin(longitudeDifference / 2) * Math.sin(longitudeDifference / 2);

        // The central angle
        double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        double distanceMiles = RADIUS_OF_EARTH * c;

        return distanceMiles <= MILE_RADIUS;
    }
}

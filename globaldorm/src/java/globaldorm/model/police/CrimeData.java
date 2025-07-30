/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package globaldorm.model.police;

/**
 *
 * @author I_NEE
 */

public class CrimeData {
    private String category;
    private String locationType;
    private Location location;
    private String context;
    private OutcomeStatus outcomeStatus;
    private String persistentID;
    private long id;
    private String locationSubtype;
    private String month;

    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }

    public String getLocationType() { return locationType; }
    public void setLocationType(String locationType) { this.locationType = locationType; }

    public Location getLocation() { return location; }
    public void setLocation(Location location) { this.location = location; }

    public String getContext() { return context; }
    public void setContext(String context) { this.context = context; }

    public OutcomeStatus getOutcomeStatus() { return outcomeStatus; }
    public void setOutcomeStatus(OutcomeStatus outcomeStatus) { this.outcomeStatus = outcomeStatus; }

    public String getPersistentID() { return persistentID; }
    public void setPersistentID(String persistentID) { this.persistentID = persistentID; }

    public long getId() { return id; }
    public void setId(long id) { this.id = id; }

    public String getLocationSubtype() { return locationSubtype; }
    public void setLocationSubtype(String locationSubtype) { this.locationSubtype = locationSubtype; }

    public String getMonth() { return month; }
    public void setMonth(String month) { this.month = month; }
}
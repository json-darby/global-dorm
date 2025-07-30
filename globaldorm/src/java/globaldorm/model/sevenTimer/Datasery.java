/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package globaldorm.model.sevenTimer;

import com.google.gson.annotations.SerializedName;

/**
 *
 * @author I_NEE
 */

public class Datasery {
    @SerializedName("date")
    private long date;

    @SerializedName("weather")
    private String weather;

    @SerializedName("temp2m")
    private Temp2M temp2M;

    @SerializedName("wind10m_max")
    private long wind10mMax;

    public long getDate() { return date; }
    public void setDate(long date) { this.date = date; }

    public String getWeather() { return weather; }
    public void setWeather(String weather) { this.weather = weather; }

    public Temp2M getTemp2M() { return temp2M; }
    public void setTemp2M(Temp2M temp2M) { this.temp2M = temp2M; }

    public long getWind10mMax() { return wind10mMax; }
    public void setWind10mMax(long wind10mMax) { this.wind10mMax = wind10mMax; }
}
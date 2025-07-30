/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package globaldorm.model.openMeteo;

import com.google.gson.annotations.SerializedName;
import java.util.List;

/**
 *
 * @author I_NEE
 */

public class WeatherDataAlternative {
    @SerializedName("daily")
    private DailyWeather daily;

    public DailyWeather getDaily() {
        return daily;
    }

    public void setDaily(DailyWeather daily) {
        this.daily = daily;
    }

    public static class DailyWeather {
        @SerializedName("time")
        private List<String> time;

        @SerializedName("temperature_2m_max")
        private List<Float> tempMax;

        @SerializedName("temperature_2m_min")
        private List<Float> tempMin;

        @SerializedName("weather_code")
        private List<Integer> weatherCode;

        public List<String> getTime() {
            return time;
        }

        public void setTime(List<String> time) {
            this.time = time;
        }

        public List<Float> getTempMax() {
            return tempMax;
        }

        public void setTempMax(List<Float> tempMax) {
            this.tempMax = tempMax;
        }

        public List<Float> getTempMin() {
            return tempMin;
        }

        public void setTempMin(List<Float> tempMin) {
            this.tempMin = tempMin;
        }

        public List<Integer> getWeatherCode() {
            return weatherCode;
        }

        public void setWeatherCode(List<Integer> weatherCode) {
            this.weatherCode = weatherCode;
        }
    }
}

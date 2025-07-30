/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package globaldorm.model.sevenTimer;

import java.util.List;

import com.google.gson.annotations.SerializedName;

/**
 *
 * @author I_NEE
 */

public class WeatherData {
    @SerializedName("product")
    private String product;

    @SerializedName("init")
    private String init;

    @SerializedName("dataseries")
    private List<Datasery> dataseries;

    public String getProduct() { return product; }
    public void setProduct(String product) { this.product = product; }

    public String getInit() { return init; }
    public void setInit(String init) { this.init = init; }

    public List<Datasery> getDataseries() { return dataseries; }
    public void setDataseries(List<Datasery> dataseries) { this.dataseries = dataseries; }
}
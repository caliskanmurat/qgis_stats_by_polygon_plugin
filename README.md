# QGIS Stats by Polygon Plugin

With this plugin, it is possible to create line plots using raster band values based on selected polygon.<br/><br/>
The figures below ( *Band 1, Band 2, ..., Band 12* ) illustrates the **_NDVI_** values of an area for given time period.<br/>
The line plot graphs show the aggregated (*min, max, mean, median and std.dev.*) NDVI values of these bands based on selected polygons.

<br/>

For creating these plots, a **_raster with multiple bands_** and a **_polygon_** layer with same ***CRS*** is needed. Bands of the raster is used for the plot. If **_multiple rasters_** exist, they can be combined into **_Virtual Raster_** and thus one raster with multiple bands can be created.

<br/>

<table>
  <tr>
    <td><img width="225" src="./images/band_1.png"><br/>Band 1 (May2023)</td>
    <td><img width="225" src="./images/band_3.png"><br/>Band 3 (Jul2023)</td>
    <td><img width="225" src="./images/band_5.png"><br/>Band 5 (Sep2023)</td>
    <td><img width="225" src="./images/band_7.png"><br/>Band 7 (Nov2023)</td>
  </tr>
  <tr>    
    <td><img width="225" src="./images/band_9.png"><br/>Band 9 (Jan2024)</td>
    <td><img width="225" src="./images/band_12.png"><br/>Band 11 (Mar2024)</td>
    <td><img width="225" src="./images/band_12.png"><br/>Band 12 (Apr2024)</td>
    <td><img width="225" height="175" src="./images/legend.png">Legend</td>
  </tr> 
</table>

<br/>
<br/>

<table>
    <tr>
      <td colspan="2"><img width="475" src="./images/image_2.png"><br/>Line Plot for Mean Value of Selected Polygons</td>
      <td colspan="2"><img width="475" src="./images/image_3.png"><br/>Line Plot for Cumulative Mean Value of Selected Polygons</td>
  </tr>
</table>

<br/>

## Instructions <br/>
* Select one or more polygon,<br/>
* Click  <img width="20" src="./icon.png">  icon,<br/>
* If selected polygons are changed ***REFRESH*** button can be used to refresh the graph.

<br/>
<br/>

> [!NOTE]
> The raster and polygon data that was used to create the figures above can be found in [sample_data folder](https://github.com/caliskanmurat/qgis_stats_by_polygon_plugin/tree/main/sample_data) <br/>
> The raster data here was prepared using [Google Earth Engine](https://earthengine.google.com/) platform, and polygons were created using QGIS Software.






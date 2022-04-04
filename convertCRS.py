import geopandas as gpd

#Set CRS
crs = 'epsg:4326'

#Load Jackson County Hexes (Pre-Determined)
kcHexes = gpd.GeoDataFrame.from_file("Maps\\KCMO-JACO-Hex.geojson").to_crs(crs)

kcHexes.to_file("Maps\\TempDataForMap\\KCMO-JACO-Hex.geojson", driver = "GeoJSON")


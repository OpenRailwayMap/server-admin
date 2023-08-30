// INFO: Following variables have be modified when this page is deployed on a server
var start_latitude = 53.5; // initial latitude of the center of the map
var start_longitude = 9.95; // initial longitude of the center of the map
var start_zoom = 10; // initial zoom level
var defaultLayerName = 'local';
var maxZoom = 19; // maximum zoom level the tile server offers
// define both base maps
var baseLayers = {
    'local' : L.tileLayer('http://localhost/tiles/osm/{z}/{x}/{y}.png', {maxZoom: maxZoom, attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors'}),
    'osm.org' : L.tileLayer('https://.tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom: 19, attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, imagery CC-BY-SA'})
};
var overlays = {
{% for style in tileserver.styles -%}
    '{{ style }}' : L.tileLayer('/{{ style }}/{z}/{x}/{y}.png', {maxZoom: maxZoom, attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, rendering CC-BY-SA OpenRailwayMap'}),
{% endfor %}
};
// End of the variables which might be modified if deployed on a server

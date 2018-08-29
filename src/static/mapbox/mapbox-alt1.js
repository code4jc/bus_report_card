$(document).ready(init);

function init(jQuery) {
  CurrentYear();

  initMap();
}

function CurrentYear() {
  var thisYear = new Date().getFullYear()
  $("#currentYear").text(thisYear);
}


// Map via Mapbox GL

var mapCoordinates = [42.885441,-78.878464];
var mapZoom = 11;

var mapAccessToken = "";

var map = null;
var geocoder = null;

function initMap() {
  map = MapGL();
}

function MapGL() {
  mapboxgl.accessToken = mapAccessToken;

  // initialize map
  var newMap = new mapboxgl.Map({
      container: "map", // container id
      style: "mapbox://styles/mapbox/streets-v9", //stylesheet location
      center: [-77.04, 38.907], // starting position
      zoom: 11 // starting zoom
  });

  // geocoding
  geocoder = new mapboxgl.Geocoder({
    container: "geocoder-container" // Optional. Specify a unique container for the control to be added to.
  });

  newMap.addControl(geocoder);

  // event handlers
  newMap.on("load", mapLoaded);
  newMap.on("click", mapPopupLayer);
  newMap.on("mousemove", mapSetCursor);

  return newMap;
}

function geocoderResults(ev) {
  map.getSource("single-point").setData(ev.result.geometry);

}

function mapLoaded() {
  mapAddPoint();
  mapAddPlaces();

  // geocoding events
  geocoder.on("result", geocoderResults);
}

// After the map style has loaded on the page, add a source layer and default
// styling for a single point.
function mapAddPoint() {
  map.addSource("single-point", {
    "type": "geojson",
    "data": {
      "type": "FeatureCollection",
      "features": []
    }
  });

  map.addLayer({
    "id": "point",
    "source": "single-point",
    "type": "circle",
    "paint": {
      "circle-radius": 10,
      "circle-color": "#007cbf"
    }
  });
}

function mapAddPlaces(data) {
// Add a GeoJSON source containing place coordinates and information.
  map.addSource("places", {
    "type": "geojson",
    "data": mapData
  });

  // Add a layer showing the places.
  map.addLayer({
    "id": "places",
    "type": "symbol",
    "source": "places",
    "layout": {
      "icon-image": "{icon}-15",
      "icon-allow-overlap": true
    }
  });
}

// When a click event occurs near a place, open a popup at the location of
// the feature, with description HTML from its properties.
function mapPopupLayer(e) {
  var features = map.queryRenderedFeatures(e.point, { layers: ["point", "places"] });

  if (!features.length) {
    return;
  }

  var feature = features[0];

  // Populate the popup and set its coordinates
  // based on the feature found.
  var popup = new mapboxgl.Popup()
    .setLngLat(feature.geometry.coordinates)
    .setHTML(feature.properties.description)
    .addTo(map);
}

// Use the same approach as above to indicate that the symbols are clickable
// by changing the cursor style to 'pointer'.
function mapSetCursor(e) {
  var features = map.queryRenderedFeatures(e.point, { layers: ["point", "places"] });
  map.getCanvas().style.cursor = (features.length) ? "pointer" : "";
}

var mapData = {
  "type": "FeatureCollection",
  "features": [{
    "type": "Feature",
    "properties": {
      "description": "<strong>Make it Mount Pleasant</strong><p><a href=\"http://www.mtpleasantdc.com/makeitmtpleasant\" target=\"_blank\" title=\"Opens in a new window\">Make it Mount Pleasant</a> is a handmade and vintage market and afternoon of live entertainment and kids activities. 12:00-6:00 p.m.</p>",
      "icon": "theatre"
    },
    "geometry": {
      "type": "Point",
      "coordinates": [-77.038659, 38.931567]
    }
  }, {
    "type": "Feature",
    "properties": {
      "description": "<strong>Mad Men Season Five Finale Watch Party</strong><p>Head to Lounge 201 (201 Massachusetts Avenue NE) Sunday for a <a href=\"http://madmens5finale.eventbrite.com/\" target=\"_blank\" title=\"Opens in a new window\">Mad Men Season Five Finale Watch Party</a>, complete with 60s costume contest, Mad Men trivia, and retro food and drink. 8:00-11:00 p.m. $10 general admission, $20 admission and two hour open bar.</p>",
      "icon": "theatre"
    },
    "geometry": {
      "type": "Point",
      "coordinates": [-77.003168, 38.894651]
    }
  }, {
    "type": "Feature",
    "properties": {
      "description": "<strong>Big Backyard Beach Bash and Wine Fest</strong><p>EatBar (2761 Washington Boulevard Arlington VA) is throwing a <a href=\"http://tallulaeatbar.ticketleap.com/2012beachblanket/\" target=\"_blank\" title=\"Opens in a new window\">Big Backyard Beach Bash and Wine Fest</a> on Saturday, serving up conch fritters, fish tacos and crab sliders, and Red Apron hot dogs. 12:00-3:00 p.m. $25.grill hot dogs.</p>",
      "icon": "bar"
    },
    "geometry": {
      "type": "Point",
      "coordinates": [-77.090372, 38.881189]
    }
  }, {
    "type": "Feature",
    "properties": {
      "description": "<strong>Ballston Arts & Crafts Market</strong><p>The <a href=\"https://ballstonarts-craftsmarket.blogspot.com/\" target=\"_blank\" title=\"Opens in a new window\">Ballston Arts & Crafts Market</a> sets up shop next to the Ballston metro this Saturday for the first of five dates this summer. Nearly 35 artists and crafters will be on hand selling their wares. 10:00-4:00 p.m.</p>",
      "icon": "art-gallery"
    },
    "geometry": {
      "type": "Point",
      "coordinates": [-77.111561, 38.882342]
    }
  }, {
    "type": "Feature",
    "properties": {
      "description": "<strong>Seersucker Bike Ride and Social</strong><p>Feeling dandy? Get fancy, grab your bike, and take part in this year's <a href=\"http://dandiesandquaintrelles.com/2012/04/the-seersucker-social-is-set-for-june-9th-save-the-date-and-start-planning-your-look/\" target=\"_blank\" title=\"Opens in a new window\">Seersucker Social</a> bike ride from Dandies and Quaintrelles. After the ride enjoy a lawn party at Hillwood with jazz, cocktails, paper hat-making, and more. 11:00-7:00 p.m.</p>",
      "icon": "bicycle"
    },
    "geometry": {
      "type": "Point",
      "coordinates": [-77.052477, 38.943951]
    }
  }, {
    "type": "Feature",
    "properties": {
      "description": "<strong>Capital Pride Parade</strong><p>The annual <a href=\"http://www.capitalpride.org/parade\" target=\"_blank\" title=\"Opens in a new window\">Capital Pride Parade</a> makes its way through Dupont this Saturday. 4:30 p.m. Free.</p>",
      "icon": "star"
    },
    "geometry": {
      "type": "Point",
      "coordinates": [-77.043444, 38.909664]
    }
  }, {
    "type": "Feature",
    "properties": {
      "description": "<strong>Muhsinah</strong><p>Jazz-influenced hip hop artist <a href=\"http://www.muhsinah.com\" target=\"_blank\" title=\"Opens in a new window\">Muhsinah</a> plays the <a href=\"http://www.blackcatdc.com\">Black Cat</a> (1811 14th Street NW) tonight with <a href=\"http://www.exitclov.com\" target=\"_blank\" title=\"Opens in a new window\">Exit Clov</a> and <a href=\"http://godsilla.bandcamp.com\" target=\"_blank\" title=\"Opens in a new window\">Gods’illa</a>. 9:00 p.m. $12.</p>",
      "icon": "music"
    },
    "geometry": {
      "type": "Point",
      "coordinates": [-77.031706, 38.914581]
    }
  }, {
    "type": "Feature",
    "properties": {
      "description": "<strong>A Little Night Music</strong><p>The Arlington Players' production of Stephen Sondheim's  <a href=\"http://www.thearlingtonplayers.org/drupal-6.20/node/4661/show\" target=\"_blank\" title=\"Opens in a new window\"><em>A Little Night Music</em></a> comes to the Kogod Cradle at The Mead Center for American Theater (1101 6th Street SW) this weekend and next. 8:00 p.m.</p>",
      "icon": "music"
    },
    "geometry": {
      "type": "Point",
      "coordinates": [-77.020945, 38.878241]
    }
  }, {
    "type": "Feature",
    "properties": {
      "description": "<strong>Truckeroo</strong><p><a href=\"http://www.truckeroodc.com/www/\" target=\"_blank\">Truckeroo</a> brings dozens of food trucks, live music, and games to half and M Street SE (across from Navy Yard Metro Station) today from 11:00 a.m. to 11:00 p.m.</p>",
      "icon": "music"
    },
    "geometry": {
      "type": "Point",
      "coordinates": [-77.007481, 38.876516]
    }
  }]
};

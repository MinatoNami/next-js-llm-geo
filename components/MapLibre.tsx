import React, { useState } from "react";
import {
  Map,
  NavigationControl,
  Popup,
  useControl,
} from "react-map-gl/maplibre";
import { ScatterplotLayer } from "deck.gl";
import { MapboxOverlay as DeckOverlay } from "@deck.gl/mapbox";
import "maplibre-gl/dist/maplibre-gl.css";

// source: Natural Earth http://www.naturalearthdata.com/ via geojson.xyz
// const AIR_PORTS =
//   "https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_10m_airports.geojson";
// const MAP_STYLE =
//   "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json";

const INITIAL_VIEW_STATE = {
  latitude: 1.33026764039613,
  longitude: 103.80974175381397,
  zoom: 11,
  bearing: 0,
  pitch: 30,
};

function DeckGLOverlay(props: Object) {
  const overlay = useControl(() => new DeckOverlay(props));
  overlay.setProps(props);
  return null;
}

export default function MapLibre() {
  const [selected] = useState(null);
  const [selectedLocation, setSelectedLocation] = useState(null);

  const layers = [
    new ScatterplotLayer({
      id: "selected-location",
      data: selectedLocation ? [selectedLocation] : [],
      getPosition: (d) => [d.longitude, d.latitude],
      getFillColor: [255, 0, 0],
      getRadius: 10,
      pickable: true,
    }),
    // new GeoJsonLayer({
    //   id: "airports",
    //   data: AIR_PORTS,
    //   // Styles
    //   filled: true,
    //   pointRadiusMinPixels: 2,
    //   pointRadiusScale: 2000,
    //   getPointRadius: (f) => 11 - f.properties.scalerank,
    //   getFillColor: [255, 255, 0],
    //   getTextColor: [0, 0, 0],
    //   // Interactive props
    //   pickable: true,
    //   autoHighlight: true,
    //   onClick: (info) => setSelected(info.object),
    //   // beforeId: 'watername_ocean' // In interleaved mode, render the layer under map labels
    // }),
    // new ArcLayer({
    //   id: "arcs",
    //   data: AIR_PORTS,
    //   dataTransform: (d) =>
    //     d.features.filter((f) => f.properties.scalerank < 4),
    //   // Styles
    //   getSourcePosition: (f) => [-0.4531566, 51.4709959], // London
    //   getTargetPosition: (f) => f.geometry.coordinates,
    //   getSourceColor: [0, 128, 200],
    //   getTargetColor: [200, 0, 80],
    //   getTextColor: [0, 0, 0],
    //   getWidth: 1,
    // }),
  ];

  const handleMapClick = (event) => {
    console.log("Event", event);
    const point = event.lngLat;
    const longitude = point.lng;
    const latitude = point.lat;
    setSelectedLocation({ longitude, latitude });
    console.log(`Selected location:`, selectedLocation);
  };

  return (
    <div style={{ width: "100vw" }}>
      <Map
        initialViewState={INITIAL_VIEW_STATE}
        onClick={handleMapClick}
        mapStyle="https://api.maptiler.com/maps/streets/style.json?key=q9G2iELJlYcDN9PPIUMI"
      >
        {selected && (
          <Popup
            key={selected.properties.name}
            anchor="bottom"
            style={{ zIndex: 10 }} /* position above deck.gl canvas */
            longitude={selected.geometry.coordinates[0]}
            latitude={selected.geometry.coordinates[1]}
          >
            {selected.properties.name} ({selected.properties.abbrev})
          </Popup>
        )}
        <DeckGLOverlay layers={layers} /* interleaved*/ />
        <NavigationControl position="top-left" />
      </Map>
    </div>
  );
}

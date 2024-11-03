import React, { useState, useEffect, useCallback, useRef } from "react";
import {
  Map,
  NavigationControl,
  Popup,
  useControl,
  MapRef,
} from "react-map-gl/maplibre";
import { LineLayer, ScatterplotLayer } from "deck.gl";
import { MapboxOverlay as DeckOverlay } from "@deck.gl/mapbox";
import { FlyToInterpolator } from "@deck.gl/core";
import "maplibre-gl/dist/maplibre-gl.css";

import fetcher from "../lib/request";

// source: Natural Earth http://www.naturalearthdata.com/ via geojson.xyz
// const AIR_PORTS =
//   "https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_10m_airports.geojson";
// const MAP_STYLE =
//   "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json";

function DeckGLOverlay(props: Object) {
  const overlay = useControl(() => new DeckOverlay(props));
  overlay.setProps(props);
  return null;
}

interface Point {
  country: string;
  distance_km: number;
  latitude: number;
  longitude: number;
  name: string;
}

interface MapLibreProps {
  pointList: Point[];
}

const MapLibre: React.FC<MapLibreProp> = ({ pointList }) => {
  const mapRef = useRef<MapRef>();

  const [selected] = useState(null);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [selectedVolcano, setSelectedVolcano] = useState(null);
  const [initialViewState, setInitialViewState] = useState({
    latitude: 1.33026764039613,
    longitude: 103.80974175381397,
    zoom: 11,
    bearing: 0,
    pitch: 30,
  });

  const [lineLayers, setLineLayers] = useState([]);

  const [points, setPoints] = useState([]);

  // Used to fetch all volcano points at the start
  useEffect(() => {
    async function fetchData() {
      const response = await fetcher("/volcanoes/all");
      // console.log("Response", response);
      setPoints(response);
    }
    fetchData();
  }, []);

  // Used to fly to the first point in the list
  useEffect(() => {
    if (pointList.length > 0) {
      setLineLayers([]);
      const temp = [];
      pointList.forEach((point) => {
        temp.push(
          new LineLayer({
            id: point.name,
            data: [point],
            getTargetPosition: (d) => [d.initialLong, d.initialLat],
            getSourcePosition: (d) => [d.longitude, d.latitude],
            getFillColor: [0, 0, 0],
            onClick: (info) => setSelectedVolcano(info.object),
            getRadius: 5000,
            pickable: true,
          })
        );
      });
      setLineLayers(temp);
      mapRef.current?.flyTo({
        center: [pointList[0].longitude, pointList[0].latitude],
        duration: 2000,
      });
      setSelectedVolcano(pointList[0]);
    }
  }, [pointList]);

  const layers = [
    new ScatterplotLayer({
      id: "selected-location",
      data: selectedLocation ? [selectedLocation] : [],
      getPosition: (d) => [d.longitude, d.latitude],
      getFillColor: [255, 0, 0],
      getRadius: 10,
      // pickable: true,
    }),
    new ScatterplotLayer({
      id: "volcanoes-location",
      data: points ? points : [],
      getPosition: (d) => [d.longitude, d.latitude],
      getFillColor: [0, 255, 0],
      onClick: (info) => setSelectedVolcano(info.object),
      getRadius: 5000,
      pickable: true,
    }),
    ...lineLayers,
  ];

  // const handleMapClick = (event) => {
  //   // console.log("Event", event);
  //   const point = event.lngLat;
  //   const longitude = point.lng;
  //   const latitude = point.lat;
  //   setSelectedLocation({ longitude, latitude });
  //   // console.log(`Selected location:`, selectedLocation);
  // };

  return (
    <div style={{ width: "100vw" }}>
      <Map
        ref={mapRef}
        initialViewState={initialViewState}
        mapStyle="https://api.maptiler.com/maps/streets/style.json?key=q9G2iELJlYcDN9PPIUMI"
      >
        {selectedVolcano && (
          <Popup
            key={selectedVolcano.name}
            anchor="bottom"
            style={{ zIndex: 10 }} /* position above deck.gl canvas */
            longitude={selectedVolcano.longitude}
            latitude={selectedVolcano.latitude}
          >
            <div style={{ color: "black" }}>
              <h2>{selectedVolcano.name}</h2>
              <p>Country: {selectedVolcano.country}</p>
              <p>
                {selectedVolcano.distance
                  ? `Distance: ${selectedVolcano.distance.toFixed(2)} km`
                  : ""}
              </p>
            </div>
          </Popup>
        )}
        <DeckGLOverlay layers={layers} /* interleaved*/ />
        <NavigationControl position="top-left" />
      </Map>
    </div>
  );
};

export default MapLibre;

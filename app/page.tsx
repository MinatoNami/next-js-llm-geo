"use client";
import { useState } from "react";
import MapLibre from "../components/MapLibre";
import ChatBot from "../components/ChatBot";

export default function App() {
  type Point = {
    country: string;
    distance: number;
    name: string;
    longitude: number;
    latitude: number;
    initialLong: number;
    initialLat: number;
  };

  const [pointList, setPointList] = useState<Point[]>([]);
  return (
    <div style={{ display: "flex" }}>
      <MapLibre pointList={pointList} />
      <ChatBot setPointList={setPointList} />
    </div>
  );
}

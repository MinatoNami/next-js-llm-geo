"use client";
import { useState } from "react";
import MapLibre from "../components/MapLibre";
import ChatBot from "../components/ChatBot";

export default function App() {
  const [pointList, setPointList] = useState([]);
  return (
    <div style={{ display: "flex" }}>
      <MapLibre pointList={pointList} />
      <ChatBot pointList={pointList} setPointList={setPointList} />
    </div>
  );
}

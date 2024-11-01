"use client";
import MapLibre from "../components/MapLibre";
import ChatBot from "../components/ChatBot";

export default function App() {
  return (
    <div style={{ display: "flex" }}>
      <MapLibre />
      <ChatBot />
    </div>
  );
}

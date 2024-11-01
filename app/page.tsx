"use client";
import React, { useState } from "react";
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

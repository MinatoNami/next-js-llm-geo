import React, { useState, useRef, useEffect } from "react";
import { Send } from "lucide-react";
import fetcher from "@/lib/request";

interface Message {
  id: number;
  text: string;
  isUser: boolean;
}

type Point = {
  country: string;
  distance: number;
  name: string;
  longitude: number;
  latitude: number;
  initialLong: number;
  initialLat: number;
};

type Props = {
  setPointList: React.Dispatch<React.SetStateAction<Point[]>>;
};

const ChatBot: React.FC<Props> = ({ setPointList }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now(),
      text: inputValue,
      isUser: true,
    };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");

    // Simulate backend response
    try {
      const response = await fetcher("/chat-query", { prompt: inputValue });
      const botMessage: Message = {
        id: Date.now() + 1,
        text: response.text,
        isUser: false,
      };
      setMessages((prev) => [...prev, botMessage]);

      type ResponsePoint = {
        country: string;
        distance_km: number;
        name: string;
        longitude: number;
        latitude: number;
        initial_long: number;
        initial_lat: number;
      };
      if (response.points) {
        const newPoints = response.points.map((point: ResponsePoint) => ({
          country: point.country,
          distance: point.distance_km,
          name: point.name,
          longitude: point.longitude,
          latitude: point.latitude,
          initialLong: point.initial_long,
          initialLat: point.initial_lat,
        }));
        setPointList(newPoints);
      }
    } catch (error) {
      console.error("Error:", error);
      const errorMessage: Message = {
        id: Date.now() + 1,
        text: "Sorry, there was an error processing your request.",
        isUser: false,
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  return (
    <div className="flex flex-col h-screen w-full max-w-md bg-white shadow-lg">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${
              message.isUser ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-[70%] rounded-lg p-3 ${
                message.isUser
                  ? "bg-blue-500 text-white"
                  : "bg-gray-200 text-gray-800"
              }`}
            >
              <p className="text-sm">{message.text}</p>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <form onSubmit={handleSubmit} className="flex items-center p-4 border-t ">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Type your message..."
          className="flex-1 p-2 border rounded-l-md focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-gray-500 text-gray-800"
          aria-label="Type your message"
        />
        <button
          type="submit"
          className="bg-blue-500 text-white p-2 rounded-r-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          aria-label="Send message"
        >
          <Send size={20} />
        </button>
      </form>
    </div>
  );
};

export default ChatBot;

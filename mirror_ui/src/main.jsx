import React from "react";
import { createRoot } from "react-dom/client";
import "./styles/tailwind.css";
import "./styles/magia_dorada.css";
import App from "./App.jsx";

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

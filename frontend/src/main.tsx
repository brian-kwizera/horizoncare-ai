import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
// @ts-ignore TypeScript does not resolve CSS side-effect imports.
import "./style.css";

const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error("Could not find the root element in index.html");
}

createRoot(rootElement).render(
  <StrictMode>
    <App />
  </StrictMode>,
);

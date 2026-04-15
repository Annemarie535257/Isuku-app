import { Component, StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";

class AppErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, errorMessage: "" };
  }

  static getDerivedStateFromError(error) {
    return {
      hasError: true,
      errorMessage: error?.message || "Unknown runtime error",
    };
  }

  componentDidCatch(error, info) {
    console.error("App render error:", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: "24px", fontFamily: "sans-serif" }}>
          <h1>Isuku frontend failed to render</h1>
          <p>{this.state.errorMessage}</p>
        </div>
      );
    }

    return this.props.children;
  }
}

window.addEventListener("error", (event) => {
  const root = document.getElementById("root");
  if (root && root.childElementCount === 0) {
    root.innerHTML = `
      <div style="padding:24px;font-family:sans-serif;">
        <h1>Isuku frontend runtime error</h1>
        <p>${event?.error?.message || event?.message || "Unknown error"}</p>
      </div>
    `;
  }
});

window.addEventListener("unhandledrejection", (event) => {
  const root = document.getElementById("root");
  if (root && root.childElementCount === 0) {
    root.innerHTML = `
      <div style="padding:24px;font-family:sans-serif;">
        <h1>Isuku frontend runtime error</h1>
        <p>${event?.reason?.message || String(event?.reason || "Unhandled promise rejection")}</p>
      </div>
    `;
  }
});

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <AppErrorBoundary>
      <App />
    </AppErrorBoundary>
  </StrictMode>
);

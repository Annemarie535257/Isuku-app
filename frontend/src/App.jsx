import { useEffect } from "react";

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "https://isuku-app.onrender.com"
).replace(/\/$/, "");

const LANDING_URL = `${API_BASE_URL}/`;

function App() {
  useEffect(() => {
    window.location.replace(LANDING_URL);
  }, []);

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        padding: "24px",
        fontFamily: "Sora, Segoe UI, sans-serif",
        background:
          "radial-gradient(1200px 600px at 20% 10%, rgba(91, 143, 61, 0.18), transparent 55%), linear-gradient(135deg, #edf4e6 0%, #d8e7c9 50%, #edf4e6 100%)",
        color: "#1f2937",
      }}
    >
      <main
        style={{
          maxWidth: "720px",
          width: "100%",
          background: "rgba(255, 255, 255, 0.88)",
          border: "1px solid rgba(63, 111, 42, 0.18)",
          borderRadius: "24px",
          padding: "32px",
          boxShadow: "0 24px 60px rgba(31, 41, 55, 0.18)",
          textAlign: "center",
          backdropFilter: "blur(10px)",
        }}
      >
        <p
          style={{
            margin: 0,
            fontSize: "0.78rem",
            fontWeight: 700,
            letterSpacing: "0.18em",
            textTransform: "uppercase",
            color: "#3f6f2a",
          }}
        >
          Isuku App
        </p>
        <h1 style={{ margin: "14px 0 12px", fontSize: "clamp(2rem, 4vw, 3.2rem)", lineHeight: 1.05 }}>
          Opening the landing page
        </h1>
        <p style={{ margin: "0 auto", maxWidth: "56ch", color: "#4b5563", fontSize: "1rem", lineHeight: 1.6 }}>
          If the page does not redirect automatically, use the button below to open the Django landing page.
        </p>
        <a
          href={LANDING_URL}
          style={{
            display: "inline-block",
            marginTop: "24px",
            padding: "14px 22px",
            borderRadius: "999px",
            background: "linear-gradient(120deg, #3f6f2a, #5b8f3d)",
            color: "#f5fbf0",
            textDecoration: "none",
            fontWeight: 700,
          }}
        >
          Open landing page
        </a>
      </main>
    </div>
  );
}

export default App;

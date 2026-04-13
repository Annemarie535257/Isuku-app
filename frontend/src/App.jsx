import { useEffect, useMemo, useRef, useState } from "react";

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "https://isuku-app.onrender.com"
).replace(/\/$/, "");

const CHAT_GREETINGS = {
  en: "Hello! I am Isuku Assistant. Ask me about pickup, sorting, or collectors.",
  rw: "Muraho! Ndi Isuku Assistant. Nyibaze ku gusaba gukusanya, gutondeka imyanda, cyangwa abakusanya.",
  fr: "Bonjour ! Je suis Isuku Assistant. Posez-moi des questions sur la collecte, le tri ou les collecteurs.",
};

const CHAT_PLACEHOLDERS = {
  en: "Ask about pickup, sorting, or routes",
  rw: "Baza ku gukusanya, gutondeka, cyangwa inzira",
  fr: "Posez une question sur la collecte, le tri ou les trajets",
};

function App() {
  const [healthText, setHealthText] = useState("Idle");
  const [analysisText, setAnalysisText] = useState("No analysis yet");
  const [previewUrl, setPreviewUrl] = useState("");
  const [selectedName, setSelectedName] = useState("No image selected");
  const [isBusy, setIsBusy] = useState(false);
  const [chatLanguage, setChatLanguage] = useState("en");
  const [chatText, setChatText] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [chatMessages, setChatMessages] = useState([
    {
      role: "bot",
      text: CHAT_GREETINGS.en,
    },
  ]);

  const galleryInputRef = useRef(null);
  const cameraInputRef = useRef(null);
  const selectedFileRef = useRef(null);

  const apiTag = useMemo(() => `API: ${API_BASE_URL}`, []);

  useEffect(() => {
    setChatMessages((previousMessages) => {
      if (
        previousMessages.length === 1 &&
        previousMessages[0]?.role === "bot" &&
        Object.values(CHAT_GREETINGS).includes(previousMessages[0].text)
      ) {
        return [{ role: "bot", text: CHAT_GREETINGS[chatLanguage] || CHAT_GREETINGS.en }];
      }

      return previousMessages;
    });
  }, [chatLanguage]);

  const setSelectedFile = (file) => {
    selectedFileRef.current = file || null;
    if (!file) {
      setSelectedName("No image selected");
      setPreviewUrl("");
      return;
    }

    setSelectedName(file.name || "camera-image.jpg");
    const tempUrl = URL.createObjectURL(file);
    setPreviewUrl(tempUrl);
  };

  const checkBackend = async () => {
    setHealthText("Checking...");
    try {
      const response = await fetch(`${API_BASE_URL}/api/districts/?province_id=1`);
      const body = await response.text();
      setHealthText(`Status: ${response.status}\n${body.slice(0, 600)}`);
    } catch (error) {
      setHealthText(`Error: ${error.message}`);
    }
  };

  const analyzeImage = async () => {
    const file = selectedFileRef.current;
    if (!file) {
      setAnalysisText("Please upload or capture a photo first.");
      return;
    }

    setIsBusy(true);
    setAnalysisText("Analyzing...");

    const formData = new FormData();
    formData.append("waste_image", file);

    try {
      const response = await fetch(`${API_BASE_URL}/api/analyze-waste-image/`, {
        method: "POST",
        body: formData,
      });
      const payload = await response.json();
      setAnalysisText(JSON.stringify(payload, null, 2));
    } catch (error) {
      setAnalysisText(`Error: ${error.message}`);
    } finally {
      setIsBusy(false);
    }
  };

  const sendChatMessage = async () => {
    const question = chatText.trim();
    if (!question || chatLoading) {
      return;
    }

    setChatMessages((prev) => [...prev, { role: "user", text: question }]);
    setChatText("");
    setChatLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/chatbot/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question, language: chatLanguage }),
      });
      const payload = await response.json();

      if (!response.ok || !payload.success) {
        throw new Error(payload.error || "Chatbot request failed");
      }

      setChatMessages((prev) => [...prev, { role: "bot", text: payload.response }]);
    } catch (error) {
      setChatMessages((prev) => [
        ...prev,
        { role: "bot", text: `I am having trouble right now: ${error.message}` },
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  return (
    <div className="shell">
      <div className="blur orb-a" />
      <div className="blur orb-b" />
      <main className="layout">
        <header className="hero">
          <img
            className="logo"
            src="https://isuku-app.onrender.com/static/images/logo%201.png"
            alt="Isuku logo"
          />
          <p className="tag">Isuku React Frontend</p>
          <h1>Responsive frontend separated from Django backend</h1>
          <p className="subtitle">
            This app runs on Netlify and calls APIs from Render.
          </p>
          <p className="api-badge">{apiTag}</p>
        </header>

        <section className="grid">
          <article className="card">
            <h2>Backend connectivity</h2>
            <p className="hint">Quick check that Netlify frontend reaches Render APIs.</p>
            <button className="btn" onClick={checkBackend}>Check backend</button>
            <pre className="output">{healthText}</pre>
          </article>

          <article className="card">
            <h2>AI waste image analyzer</h2>
            <p className="hint">Use gallery or camera. Then run analysis.</p>

            <input
              ref={galleryInputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(event) => setSelectedFile(event.target.files?.[0])}
            />
            <input
              ref={cameraInputRef}
              type="file"
              accept="image/*"
              capture="environment"
              className="hidden"
              onChange={(event) => setSelectedFile(event.target.files?.[0])}
            />

            <div className="actions">
              <button
                className="btn secondary"
                onClick={() => galleryInputRef.current?.click()}
              >
                Upload from device
              </button>
              <button className="btn" onClick={() => cameraInputRef.current?.click()}>
                Take photo now
              </button>
            </div>

            <p className="file-name">{selectedName}</p>
            {previewUrl && <img className="preview" src={previewUrl} alt="Selected waste" />}

            <button className="btn analyze" disabled={isBusy} onClick={analyzeImage}>
              {isBusy ? "Analyzing..." : "Analyze image"}
            </button>
            <pre className="output">{analysisText}</pre>
          </article>

          <article className="card chat-card">
            <h2>Isuku Assistant</h2>
            <p className="hint">Connected to backend endpoint: /api/chatbot/</p>

            <div className="chat-toolbar">
              <label className="chat-language-label" htmlFor="chat-language-select">
                Response language
              </label>
              <select
                id="chat-language-select"
                className="chat-language-select"
                value={chatLanguage}
                onChange={(event) => setChatLanguage(event.target.value)}
              >
                <option value="en">English</option>
                <option value="rw">Kinyarwanda</option>
                <option value="fr">Français</option>
              </select>
            </div>

            <div className="chat-stream">
              {chatMessages.map((message, index) => (
                <div key={index} className={`chat-bubble ${message.role}`}>
                  {message.text}
                </div>
              ))}
              {chatLoading && <div className="chat-bubble bot">Thinking...</div>}
            </div>

            <div className="chat-controls">
              <input
                value={chatText}
                onChange={(event) => setChatText(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    sendChatMessage();
                  }
                }}
                placeholder={CHAT_PLACEHOLDERS[chatLanguage] || CHAT_PLACEHOLDERS.en}
              />
              <button className="btn" onClick={sendChatMessage} disabled={chatLoading}>
                Send
              </button>
            </div>
          </article>
        </section>
      </main>
    </div>
  );
}

export default App;

import { useState, useEffect } from "react";

function App() {
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);
  const [options, setOptions] = useState([]);
  const [showInput, setShowInput] = useState(false);
  const [spamBlocked, setSpamBlocked] = useState(false);
  const [submissionLocked, setSubmissionLocked] = useState(false);
  const [loading, setLoading] = useState(false);
  const [databaseError, setDatabaseError] = useState("");

  // ✅ GLOBAL BANNER (success / error / info)
  const [banner, setBanner] = useState({
    type: "",
    text: ""
  });
  
  // Fetch options
  useEffect(() => {
    const fetchOptions = async () => {

      try {

        const res = await fetch("http://127.0.0.1:5000/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ init: true }),
        });

        const data = await res.json();

        // Database error
        if (data.reply?.includes("Database error")) {
          setDatabaseError("❌ Database error: Cannot connect to MySQL.");
          return;
        }

        setOptions(data.options || []);

      } catch (err) {

        // Backend not running
        setDatabaseError(
          "❌ Backend is not running. Please start the Flask backend server."
        );

      }
    };

    fetchOptions();

  }, []);

  // word count
  const countWords = (text) =>
    text.trim().split(/\s+/).filter(Boolean).length;

  // clear banner helper
  const showBanner = (type, text) => {
    setBanner({ type, text });

    setTimeout(() => {
      setBanner({ type: "", text: "" });
    }, 7000);
  };

  // SEND MESSAGE
  const sendMessage = async (msg = message) => {
    // ✅ INTERNET CHECK
    if (!navigator.onLine) {
      showBanner(
        "error",
        "❌ No internet connection. Please check your network."
      );
      return;
    }
    
    if (!msg.trim()) return;

    // 300 word limit
    if (countWords(msg) > 300) {
      setChat((prev) => [
        ...prev,
        {
          user: msg,
          bot: "⚠️ Message too long. Please limit to 300 words.",
        },
      ]);
      return;
    }

    setLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg }),
      });

      if (!res.ok) throw new Error("Server error");

      const data = await res.json();

      // chat update
      setChat((prev) => [
        ...prev,
        {
          user: msg,
          bot: data.reply || "No response from server.",
        },
      ]);

      // ✅ SUCCESS BANNER ONLY FOR "Other" INPUT
      if (msg === message) {
        showBanner("success", "✅ Message sent successfully");
      }

      // spam / lock handling (KEEP YOUR LOGIC)
      if (data.reply.includes("24 hours")) {
        setSpamBlocked(true);
        setShowInput(false);
        showBanner("error", "⏳ Blocked for 24 hours.  Urgent Contact 000-1111111");
      } else if (data.reply.includes("72 hours")) {
        setSubmissionLocked(true);
        setShowInput(false);
        showBanner("error", "⏳ You already submitted a request.  Urgent Contact 000-1111111");
      }

      // Gemini errors
      if (data.reply.includes("API key invalid")) {
        showBanner("error", "❌ Gemini API key invalid. Please check your token.");
      } else if (data.reply.includes("quota exceeded")) {
        showBanner("error", "⚠️ Gemini quota exceeded. Try later.");
      } else if (data.reply.includes("service unavailable")) {
        showBanner("error", "⚠️ Gemini service unavailable. Try again later.");
      }

      setMessage("");
    } catch (err) {
      console.error(err);

      setChat((prev) => [
        ...prev,
        {
          user: msg,
          bot: "⚠️ Server error.",
        },
      ]);

      showBanner("error", "⚠️ Server error.");
    } finally {
      setLoading(false);
    }
  };

      if (databaseError) {
        return (
          <div
            style={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              height: "100vh",
              fontSize: "22px",
              color: "red",
              fontWeight: "bold",
              textAlign: "center",
              padding: "20px"
            }}
          >
            {databaseError}
          </div>
        );
      }

  return (
    <div className="app-container">
      <div className="header">Smart Assist AI Bot 🤖</div>

      {/* ✅ TOP BANNER (ONLY HERE) */}
      {banner.text && (
        <div
          style={{
            padding: "10px",
            margin: "10px 0",
            borderRadius: "8px",
            background:
              banner.type === "success"
                ? "#d1fae5"
                : banner.type === "error"
                ? "#fee2e2"
                : "#e5e7eb",
            color: "#111",
            textAlign: "center"   // ✅ Center text
          }}
        >
          {banner.text}
        </div>
      )}

      {/* OPTIONS */}
      <div className="options">
        {options.map((opt, i) => (
          <button
            key={i}
            onClick={() => {
              // LOCKED STATE
              if (submissionLocked && opt === "Other") {
                showBanner(
                  "error",
                  "⏳ You already submitted a request wait for 72 hours. Urgent Contact 000-1111111"
                );
                setShowInput(false);
                return;
              }

              if (spamBlocked && opt === "Other") {
                showBanner(
                  "error",
                  "🚫 You are blocked for 24 hours."
                );
                setShowInput(false);
                return;
              }

              if (opt === "Other") {
                setShowInput(true);
                return;
              }

              setShowInput(false);
              sendMessage(opt);
            }}
          >
            {opt}
          </button>
        ))}
      </div>

      {/* CHAT */}
      <div className="chat-box">
        {chat.map((c, index) => (
          <div key={index}>
            <div className="message user">
              <b>You:</b> {c.user}
            </div>
            <div className="message bot">
              <b>Bot:</b> {c.bot}
            </div>
          </div>
        ))}
      </div>

      {/* INPUT BOX */}
      {showInput && !spamBlocked && !submissionLocked && (
        <div className="input-area">
          <input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Please describe your issue clearly .... (max 300 words)"
            onKeyDown={(e) => {
              if (e.key === "Enter") sendMessage();
            }}
          />

          <button onClick={() => sendMessage()} disabled={loading}>
            {loading ? "Sending..." : "Send"}
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
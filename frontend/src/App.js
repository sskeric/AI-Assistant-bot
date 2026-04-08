import { useState } from "react";

function App() {
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);

  const sendMessage = async () => {
  const res = await fetch("http://127.0.0.1:5000/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
  });

  const data = await res.json();

  setChat([...chat, { user: message, bot: data.reply }]);
  setMessage("");
};

  return (
    <div className="app-container">
    
    <div className="header">
      Smart Assist AI Bot 🤖
    </div>

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

    <div className="input-area">
      <input
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Type your question..."
      />

      <button onClick={sendMessage}>
        Send
      </button>
    </div>

    </div>
  );
}

export default App;
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
    <div style={{ padding: "20px" }}>
      <h1>Smart Assist AI Bot</h1>

      <div style={{ marginBottom: "20px" }}>
        {chat.map((c, index) => (
          <div key={index}>
            <p><b>User:</b> {c.user}</p>
            <p><b>Bot:</b> {c.bot}</p>
          </div>
        ))}
      </div>

      <input
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Type your problem..."
      />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
}

export default App;
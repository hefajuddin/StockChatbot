// import React, { useState } from "react";
// import { useNavigate } from "react-router-dom";
// import api from "../api";
// import ChatBox from "../components/ChatBox";

// /** simple html escaper */
// function escapeHtml(unsafe) {
//   if (unsafe === null || unsafe === undefined) return "";
//   return String(unsafe)
//     .replaceAll("&", "&amp;")
//     .replaceAll("<", "&lt;")
//     .replaceAll(">", "&gt;")
//     .replaceAll('"', "&quot;")
//     .replaceAll("'", "&#039;");
// }

// /** format price info — returns HTML string */
// export function formatPriceInfo(item) {
//   if (!item) return "";

//   if (Array.isArray(item.buySellDetails)) {
//     const rows = item.buySellDetails
//       .map((row) => {
//         const buyPrice = escapeHtml(row.buyPrice);
//         const buyVolume = escapeHtml(row.buyVolume);
//         const buyerCount = escapeHtml(row.buyerCount);
//         const sellPrice = escapeHtml(row.sellPrice);
//         const sellVolume = escapeHtml(row.sellVolume);
//         const sellerCount = escapeHtml(row.sellerCount);

//         return `<tr>
//           <td class="buy">${buyPrice}</td>
//           <td class="buy">${buyVolume}</td>
//           <td class="buy">${buyerCount}</td>
//           <td class="sell">${sellPrice}</td>
//           <td class="sell">${sellVolume}</td>
//           <td class="sell">${sellerCount}</td>
//         </tr>`;
//       })
//       .join("");

//     return `<table class="buy-sell-table">
//       <thead>
//         <tr>
//           <th class="buy">BUY PRICE</th>
//           <th class="buy">BUY VOL</th>
//           <th class="buy">BUYERS</th>
//           <th class="sell">SELL PRICE</th>
//           <th class="sell">SELL VOL</th>
//           <th class="sell">SELLERS</th>
//         </tr>
//       </thead>
//       <tbody>${rows}</tbody>
//     </table>`;
//   }

//   if (typeof item === "object") {
//     const entries = Object.entries(item)
//       .map(([k, v]) => `${escapeHtml(k.toUpperCase())}: ${escapeHtml(v)}`)
//       .join(", ");
//     return `<div>${entries}</div>`;
//   }

//   return `<div>${escapeHtml(item)}</div>`;
// }

// export default function ChatPage() {
//   const [messages, setMessages] = useState([]);
//   const [input, setInput] = useState("");
//   const navigate = useNavigate();

//   const sendMessage = async () => {
//     if (!input.trim()) return;

//     // Add user message
//     setMessages((prev) => [...prev, { sender: "user", text: input }]);
//     setInput("");

//     try {
//       const res = await api.post("/predict_batch", { inputs: [{ text: input }] });
//       const result = res?.data?.results?.[0];

//       const recommendResponse = result?.results?.generalResponse?.recommendResponse ?? [];
//       const priceResponse = result?.results?.generalResponse?.priceResponse ?? [];
//       const priceList = result?.priceList ?? [];

//       const botMsg = { sender: "bot", recommendResponse, priceResponse, priceList };
//       setMessages((prev) => [...prev, botMsg]);
//     } catch (err) {
//       if (err.response?.status === 401) {
//         alert("Session expired. Please login again.");
//         navigate("/");
//       } else {
//         setMessages((prev) => [...prev, { sender: "bot", text: "Error fetching response." }]);
//       }
//     }
//   };

//   const handleKeyDown = (e) => {
//     if (e.key === "Enter" && !e.shiftKey) {
//       e.preventDefault();
//       sendMessage();
//     }
//   };

//   return (
//     <div style={{ maxWidth: "900px", margin: "2rem auto", textAlign: "center" }}>
//       <h2>Stock Chatbot</h2>
//       <ChatBox messages={messages} />
//       <div style={{ display: "flex", justifyContent: "center", gap: "0.5rem" }}>
//         <textarea
//           style={{ width: "70%", padding: "0.5rem" }}
//           value={input}
//           onChange={(e) => setInput(e.target.value)}
//           onKeyDown={handleKeyDown}
//           placeholder="Type a message (Enter to send)"
//           rows={2}
//         />
//         <button style={{ padding: "0.6rem 1rem" }} onClick={sendMessage}>
//           Send
//         </button>
//       </div>
//     </div>
//   );
// }








import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";
import ChatBox from "../components/ChatBox";

/** simple html escaper */
function escapeHtml(unsafe) {
  if (unsafe === null || unsafe === undefined) return "";
  return String(unsafe)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

/** format price info — returns HTML string */
export function formatPriceInfo(item) {
  if (!item) return "";

  if (Array.isArray(item.buySellDetails)) {
    const rows = item.buySellDetails
      .map((row) => {
        const buyPrice = escapeHtml(row.buyPrice);
        const buyVolume = escapeHtml(row.buyVolume);
        const buyerCount = escapeHtml(row.buyerCount);
        const sellPrice = escapeHtml(row.sellPrice);
        const sellVolume = escapeHtml(row.sellVolume);
        const sellerCount = escapeHtml(row.sellerCount);

        return `<tr>
          <td class="buy">${buyPrice}</td>
          <td class="buy">${buyVolume}</td>
          <td class="buy">${buyerCount}</td>
          <td class="sell">${sellPrice}</td>
          <td class="sell">${sellVolume}</td>
          <td class="sell">${sellerCount}</td>
        </tr>`;
      })
      .join("");

    return `<table class="buy-sell-table">
      <thead>
        <tr>
          <th class="buy">BUY PRICE</th>
          <th class="buy">BUY VOL</th>
          <th class="buy">BUYERS</th>
          <th class="sell">SELL PRICE</th>
          <th class="sell">SELL VOL</th>
          <th class="sell">SELLERS</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>`;
  }

  if (typeof item === "object") {
    const entries = Object.entries(item)
      .map(([k, v]) => `${escapeHtml(k.toUpperCase())}: ${escapeHtml(v)}`)
      .join(", ");
    return `<div>${entries}</div>`;
  }

  return `<div>${escapeHtml(item)}</div>`;
}

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const navigate = useNavigate();

  const sendMessage = async () => {
    if (!input.trim()) return;

    // Add user message
    setMessages((prev) => [...prev, { sender: "user", text: input }]);
    setInput("");

    try {
      const res = await api.post("/predict_batch", { inputs: [{ text: input }] });
      const result = res?.data?.results?.[0];

      const recommendResponse = result?.results?.generalResponse?.recommendResponse ?? [];
      const priceResponse = result?.results?.generalResponse?.priceResponse ?? [];
      const priceList = result?.priceList ?? [];

      const botMsg = { sender: "bot", recommendResponse, priceResponse, priceList };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      if (err.response?.status === 401) {
        alert("Session expired. Please login again.");
        navigate("/");
      } else {
        setMessages((prev) => [...prev, { sender: "bot", text: "Error fetching response." }]);
      }
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // --- New logout function ---
const handleLogout = async () => {
  const token = localStorage.getItem("accessToken");
  if (!token) {
    alert("No session found");
    navigate("/");
    return;
  }

  try {
    await api.post("/logout", null, {
      headers: { Authorization: `Bearer ${token}` }
    });
    localStorage.removeItem("accessToken");
    localStorage.removeItem("user_id"); // যদি আগে রাখা থাকে
    navigate("/");
  } catch (err) {
    console.error(err);
    alert("Logout failed. Try again.");
  }
};

  return (
    <div style={{ maxWidth: "900px", margin: "2rem auto", textAlign: "center", position: "relative" }}>
      {/* Logout button on top right */}
      <button
        onClick={handleLogout}
        style={{
          position: "absolute",
          top: "1rem",
          right: "1rem",
          padding: "0.5rem 1rem",
          cursor: "pointer",
        }}
      >
        Logout
      </button>

      <h2>Stock Chatbot</h2>
      <ChatBox messages={messages} />
      <div style={{ display: "flex", justifyContent: "center", gap: "0.5rem" }}>
        <textarea
          style={{ width: "70%", padding: "0.5rem" }}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message (Enter to send)"
          rows={2}
        />
        <button style={{ padding: "0.6rem 1rem" }} onClick={sendMessage}>
          Send
        </button>
      </div>
    </div>
  );
}

import { useState } from "react";
import api from "../api";
import { useNavigate } from "react-router-dom";
import "./LoginPage.css";   // CSS ফাইল লোড

export default function LoginPage() {
  const [loginId, setLoginId] = useState("");
  const [password, setPassword] = useState("");
  const [deviceId, setDeviceId] = useState("c5d334f5-5c81-41f1-8b77-87485242424c");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await api.post("/login", { loginId, password, deviceId });
      localStorage.setItem("accessToken", res.data.token);
      navigate("/chat");
    } catch (err) {
      setError("Login failed");
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2 className="login-title">Welcome Back</h2>
        <form onSubmit={handleSubmit} className="login-form">
          <input
            className="login-input"
            placeholder="User ID"
            value={loginId}
            onChange={(e) => setLoginId(e.target.value)}
          />
          <input
            className="login-input"
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button className="login-btn" type="submit">
            Login
          </button>
          {error && <p className="login-error">{error}</p>}
        </form>
      </div>
    </div>
  );
}

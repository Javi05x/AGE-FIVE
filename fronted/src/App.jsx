import React from "react";
import { Routes, Route, Link } from "react-router-dom";
import Search from "./pages/Search.jsx";
import Player from "./pages/Player.jsx";

export default function App() {
  return (
    <div style={{ fontFamily: "system-ui", padding: 16 }}>
      <header style={{ display: "flex", gap: 12, alignItems: "center", marginBottom: 16 }}>
        <Link to="/" style={{ textDecoration: "none" }}>
          <h2 style={{ margin: 0 }}>AGE-FIVE</h2>
        </Link>
      </header>

      <Routes>
        <Route path="/" element={<Search />} />
        <Route path="/player" element={<Player />} />
      </Routes>
    </div>
  );
}

import { useEffect, useState } from "react";
import adminApi from "../services/adminApi";

function Dashboard() {

  const [stats, setStats] = useState(null);
  const [chats, setChats] = useState([]); // ✅ FIXED (inside component)

  useEffect(() => {
    fetchStats();
    fetchChats();
  }, []);

  const fetchStats = async () => {
    try {
      const res = await adminApi.get("/admin/stats");
      setStats(res.data);
    } catch (err) {
      console.log("Error loading stats", err);
    }
  };

  const fetchChats = async () => {
    try {
      const res = await adminApi.get("/admin/recent-chats");
      setChats(res.data);
    } catch (err) {
      console.log("Error loading chats", err);
    }
  };

  if (!stats) {
    return <h2>Loading dashboard...</h2>;
  }

  return (
    <div style={{ padding: "20px" }}>
      <h1>Admin Dashboard</h1>

      {/* ================= STATS ================= */}
      <div style={{ display: "flex", gap: "20px", marginTop: "20px" }}>

        <div style={cardStyle}>
          <h3>Total Sessions</h3>
          <p>{stats.total_sessions}</p>
        </div>

        <div style={cardStyle}>
          <h3>Active Sessions</h3>
          <p>{stats.active_sessions}</p>
        </div>

        <div style={cardStyle}>
          <h3>Total Messages</h3>
          <p>{stats.total_messages}</p>
        </div>

      </div>

      {/* ================= RECENT CHATS ================= */}
      <div style={{ marginTop: "30px" }}>
        <h2>Recent Chats</h2>

        {chats.map((c, i) => (
          <div
            key={i}
            style={{
              padding: "10px",
              borderBottom: "1px solid #ddd"
            }}
          >
            <b>{c.session_id}</b> ({c.role})
            <div>{c.message}</div>
          </div>
        ))}
      </div>

    </div>
  );
}

const cardStyle = {
  padding: "20px",
  borderRadius: "10px",
  background: "#f3f4f6",
  minWidth: "150px",
  textAlign: "center",
  boxShadow: "0 2px 6px rgba(0,0,0,0.1)"
};

export default Dashboard;
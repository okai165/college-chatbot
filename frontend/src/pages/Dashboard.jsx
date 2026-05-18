import { useEffect, useState } from "react";
import adminApi from "../services/adminApi";

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [days, setDays] = useState(1); // ✅ default 1 day

  useEffect(() => {
    fetchStats(days);
  }, [days]);

  const fetchStats = async (d) => {
    try {
      const res = await adminApi.get(`/admin/stats?days=${d}`);
      setStats(res.data);
    } catch (err) {
      console.log("Error loading stats", err);
    }
  };

  if (!stats) {
    return (
      <div style={pageStyle}>
        <h2>Loading dashboard...</h2>
      </div>
    );
  }

  return (
    <div style={pageStyle}>
      {/* शीर्ष row: title + filter */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: "12px",
          flexWrap: "wrap",
        }}
      >
        <h1 style={{ margin: 0 }}>Admin Dashboard</h1>

        {/* ✅ FILTER */}
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <span style={{ fontWeight: "600" }}>Range:</span>
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            style={{
              padding: "8px 10px",
              borderRadius: "8px",
              border: "none",
              outline: "none",
              cursor: "pointer",
            }}
          >
            <option value={1}>Last 1 day</option>
            <option value={3}>Last 3 days</option>
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
          </select>
        </div>
      </div>

      {/* ================= STATS ================= */}
      <div
        style={{
          display: "flex",
          gap: "12px",
          marginTop: "20px",
          flexWrap: "nowrap",
          overflowX: "auto",
          paddingBottom: "10px",
        }}
      >
        <div style={cardStyle}>
          <h3 style={cardTitleStyle}>Total Sessions</h3>
          <p style={cardValueStyle}>{stats.total_sessions}</p>
        </div>

        <div style={cardStyle}>
          <h3 style={cardTitleStyle}>Active Sessions</h3>
          <p style={cardValueStyle}>{stats.active_sessions}</p>
        </div>

        <div style={cardStyle}>
          <h3 style={cardTitleStyle}>Total Messages</h3>
          <p style={cardValueStyle}>{stats.total_messages}</p>
        </div>

        <div style={cardStyle}>
          <h3 style={cardTitleStyle}>Avg Messages / Session</h3>
          <p style={cardValueStyle}>{stats.avg_messages_per_session}</p>
        </div>
      </div>
    </div>
  );
}

const pageStyle = {
  padding: "20px",
  minHeight: "100vh",
  background: "#2563eb",
  color: "white",
};

const cardStyle = {
  padding: "16px",
  borderRadius: "10px",
  background: "white",
  color: "black",
  width: "220px",
  height: "120px",
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  alignItems: "center",
  textAlign: "center",
  boxShadow: "0 2px 10px rgba(0,0,0,0.2)",
  flex: "0 0 auto",
};

const cardTitleStyle = {
  margin: 0,
  fontSize: "16px",
};

const cardValueStyle = {
  margin: "8px 0 0",
  fontSize: "28px",
  fontWeight: "bold",
};

export default Dashboard;
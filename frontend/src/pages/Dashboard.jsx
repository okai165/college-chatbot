import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import adminApi from "../services/adminApi";
import AdminLayout from "../components/AdminLayout";

function Dashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [days, setDays] = useState(1);
  const [error, setError] = useState(null);
  const [isRefreshHover, setIsRefreshHover] = useState(false);
  const [isRetryHover, setIsRetryHover] = useState(false);

  useEffect(() => {
    fetchStats(days);
  }, [days]);

  const fetchStats = async (d) => {
    try {
      const res = await adminApi.get(`/admin/stats?days=${d}`);
      setStats(res.data);
      setError(null);
    } catch (err) {
      console.log("Error loading stats", err);
      if (err.response?.status === 401) {
        setError("Authorization required. Redirecting to login...");
        navigate("/admin");
      } else {
        setError("Unable to load dashboard stats. Please try again.");
      }
      setStats({
        total_sessions: 0,
        active_sessions: 0,
        total_messages: 0,
        avg_messages_per_session: 0,
      });
    }
  };

  if (!stats && !error) {
    return (
      <AdminLayout>
        <div style={{ padding: "20px" }}>
          <h2>Loading dashboard...</h2>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <div style={pageStyle}>
        {error && (
          <div style={errorBannerStyle}>
            <div>{error}</div>
            <button
              onClick={() => fetchStats(days)}
              onMouseEnter={() => setIsRetryHover(true)}
              onMouseLeave={() => setIsRetryHover(false)}
              style={{
                ...errorRetryButtonStyle,
                ...(isRetryHover ? errorRetryButtonHoverStyle : {}),
              }}
            >
              Retry
            </button>
          </div>
        )}

        {/* ================= HEADER ================= */}
        <div style={headerStyle}>
          <h1 style={{ margin: 0, color: "#0f172a", fontSize: "32px" }}>Admin Dashboard</h1>

          {/* FILTER */}
          <div style={filterWrapperStyle}>
            <span style={{ fontWeight: "600", color: "#0f172a" }}>Range:</span>

            <select
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              style={selectStyle}
            >
              <option value={1}>Last 1 day</option>
              <option value={3}>Last 3 days</option>
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
            </select>
            <button
              onClick={() => fetchStats(days)}
              onMouseEnter={() => setIsRefreshHover(true)}
              onMouseLeave={() => setIsRefreshHover(false)}
              style={{
                ...refreshButtonStyle,
                ...(isRefreshHover ? refreshButtonHoverStyle : {}),
              }}
            >
              Refresh
            </button>
          </div>
        </div>

        {/* ================= STATS ================= */}
        <div style={statsContainerStyle}>

          <div style={cardStyle}>
            <h3 style={cardTitleStyle}>Total Sessions</h3>
            <p style={cardValueStyle}>
              {stats.total_sessions}
            </p>
          </div>

          <div style={cardStyle}>
            <h3 style={cardTitleStyle}>Active Sessions</h3>
            <p style={cardValueStyle}>
              {stats.active_sessions}
            </p>
          </div>

          <div style={cardStyle}>
            <h3 style={cardTitleStyle}>Total Messages</h3>
            <p style={cardValueStyle}>
              {stats.total_messages}
            </p>
          </div>

          <div style={cardStyle}>
            <h3 style={cardTitleStyle}>
              Avg Messages / Session
            </h3>

            <p style={cardValueStyle}>
              {stats.avg_messages_per_session}
            </p>
          </div>

        </div>

      </div>
    </AdminLayout>
  );
}

const errorBannerStyle = {
  width: "100%",
  padding: "16px",
  marginBottom: "20px",
  borderRadius: "12px",
  background: "#fee2e2",
  color: "#991b1b",
  border: "1px solid #fecaca",
};

const pageStyle = {
  padding: "20px",
};

const headerStyle = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  gap: "20px",
  flexWrap: "wrap",
};

const filterWrapperStyle = {
  display: "flex",
  alignItems: "center",
  gap: "10px",
};

const selectStyle = {
  padding: "8px 12px",
  borderRadius: "8px",
  border: "1px solid #d1d5db",
  outline: "none",
  cursor: "pointer",
  background: "white",
  color: "#111827",
  minWidth: "170px",
};

const refreshButtonStyle = {
  marginLeft: "12px",
  padding: "10px 16px",
  borderRadius: "8px",
  border: "none",
  background: "#2563eb",
  color: "white",
  fontWeight: "600",
  cursor: "pointer",
};

const errorRetryButtonStyle = {
  marginTop: "12px",
  padding: "10px 16px",
  borderRadius: "8px",
  border: "none",
  background: "#2563eb",
  color: "white",
  fontWeight: "600",
  cursor: "pointer",
  transition: "all 0.2s ease",
};

const refreshButtonHoverStyle = {
  background: "#1d4ed8",
  transform: "translateY(-1px)",
  boxShadow: "0 8px 18px rgba(37, 99, 235, 0.25)",
};

const errorRetryButtonHoverStyle = {
  background: "#1d4ed8",
  transform: "translateY(-1px)",
  boxShadow: "0 8px 18px rgba(37, 99, 235, 0.25)",
};

const statsContainerStyle = {
  display: "flex",
  gap: "16px",
  marginTop: "25px",
  flexWrap: "nowrap",
  overflowX: "auto",
  paddingBottom: "10px",
};

const cardStyle = {
  width: "220px",
  height: "120px",
  background: "white",
  borderRadius: "12px",
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  alignItems: "center",
  textAlign: "center",
  boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
  border: "1px solid #e5e7eb",
  flex: "0 0 auto",
};

const cardTitleStyle = {
  margin: 0,
  fontSize: "16px",
  color: "#374151",
};

const cardValueStyle = {
  marginTop: "10px",
  fontSize: "28px",
  fontWeight: "bold",
  color: "#111827",
};

export default Dashboard;
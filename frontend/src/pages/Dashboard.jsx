import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import adminApi from "../services/adminApi";
import AdminLayout from "../components/AdminLayout";

import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  AreaChart,
  Area
} from "recharts";

function Dashboard() {

  const navigate = useNavigate();

  const [stats, setStats] = useState(null);

  const [days, setDays] = useState(1);

  const [error, setError] = useState(null);

  const [isRefreshHover, setIsRefreshHover] =
    useState(false);

  const [isRetryHover, setIsRetryHover] =
    useState(false);

  useEffect(() => {

    fetchStats(days);

  }, [days]);

  const fetchStats = async (d) => {

    try {

      const res = await adminApi.get(
        `/admin/stats?days=${d}`
      );

      setStats(res.data);

      setError(null);

    } catch (err) {

      console.log(
        "Error loading stats",
        err
      );

      if (err.response?.status === 401) {

        setError(
          "Authorization required. Redirecting to login..."
        );

        navigate("/admin");

      } else {

        setError(
          "Unable to load dashboard stats. Please try again."
        );
      }

      setStats({
        total_sessions: 0,
        active_sessions: 0,
        total_messages: 0,
        avg_messages_per_session: 0,
        sessions_graph: [],
        messages_graph: [],
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
              onMouseEnter={() =>
                setIsRetryHover(true)
              }
              onMouseLeave={() =>
                setIsRetryHover(false)
              }
              style={{
                ...errorRetryButtonStyle,
                ...(isRetryHover
                  ? errorRetryButtonHoverStyle
                  : {}),
              }}
            >
              Retry
            </button>

          </div>

        )}

        {/* ================= HEADER ================= */}

        <div style={headerStyle}>

          <h1 style={dashboardTitleStyle}>
            Admin Dashboard
          </h1>

          <div style={filterWrapperStyle}>

            <span style={filterTextStyle}>
              Range:
            </span>

            <select
              value={days}
              onChange={(e) =>
                setDays(Number(e.target.value))
              }
              style={selectStyle}
            >

              <option value={1}>
                Last 1 day
              </option>

              <option value={3}>
                Last 3 days
              </option>

              <option value={7}>
                Last 7 days
              </option>

              <option value={30}>
                Last 30 days
              </option>

            </select>

            <button
              onClick={() =>
                fetchStats(days)
              }
              onMouseEnter={() =>
                setIsRefreshHover(true)
              }
              onMouseLeave={() =>
                setIsRefreshHover(false)
              }
              style={{
                ...refreshButtonStyle,
                ...(isRefreshHover
                  ? refreshButtonHoverStyle
                  : {}),
              }}
            >
              Refresh
            </button>

          </div>

        </div>

        {/* ================= STATS ================= */}

        <div style={statsContainerStyle}>

          <div style={cardStyle}>
            <h3 style={cardTitleStyle}>
              Total Sessions
            </h3>

            <p style={cardValueStyle}>
              {stats.total_sessions}
            </p>
          </div>

          <div style={cardStyle}>
            <h3 style={cardTitleStyle}>
              Active Sessions
            </h3>

            <p style={cardValueStyle}>
              {stats.active_sessions}
            </p>
          </div>

          <div style={cardStyle}>
            <h3 style={cardTitleStyle}>
              Total Messages
            </h3>

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

        {/* ================= CHARTS ================= */}

        <div style={chartsWrapperStyle}>

          {/* SESSIONS GRAPH */}

          <div style={chartCardStyle}>

            <h2 style={chartTitleStyle}>
              Sessions Trend
            </h2>

            <ResponsiveContainer
              width="100%"
              height={300}
            >

              <LineChart
                data={stats.sessions_graph}
              >

                <CartesianGrid
                  strokeDasharray="3 3"
                />

                <XAxis dataKey="day" />

                <YAxis />

                <Tooltip />

                <Line
                  type="monotone"
                  dataKey="total"
                  stroke="#2563eb"
                  strokeWidth={3}
                />

              </LineChart>

            </ResponsiveContainer>

          </div>

          {/* MESSAGES GRAPH */}

          <div style={chartCardStyle}>

            <h2 style={chartTitleStyle}>
              Messages Trend
            </h2>

            <ResponsiveContainer
              width="100%"
              height={300}
            >

              <AreaChart
                data={stats.messages_graph}
              >

                <CartesianGrid
                  strokeDasharray="3 3"
                />

                <XAxis dataKey="day" />

                <YAxis />

                <Tooltip />

                <Area
                  type="monotone"
                  dataKey="total"
                  stroke="#16a34a"
                  fill="#86efac"
                />

              </AreaChart>

            </ResponsiveContainer>

          </div>

        </div>

      </div>

    </AdminLayout>
  );
}

/* ================= STYLES ================= */

const pageStyle = {
  padding: "20px",
};

const dashboardTitleStyle = {
  margin: 0,
  color: "#0f172a",
  fontSize: "34px",
  fontWeight: "700",
  cursor: "pointer",
  transition: "0.3s",
};

const errorBannerStyle = {
  width: "100%",
  padding: "16px",
  marginBottom: "20px",
  borderRadius: "12px",
  background: "#fee2e2",
  color: "#991b1b",
  border: "1px solid #fecaca",
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

const filterTextStyle = {
  fontWeight: "600",
  color: "#0f172a",
};

const selectStyle = {
  padding: "10px 14px",
  borderRadius: "10px",
  border: "1px solid #cbd5e1",
  background: "white",
  color: "#0f172a", // IMPORTANT
  fontWeight: "600",
  fontSize: "15px",
  cursor: "pointer",
  minWidth: "170px",
  outline: "none",
};

const refreshButtonStyle = {
  padding: "10px 16px",
  borderRadius: "10px",
  border: "none",
  background: "#2563eb",
  color: "white",
  fontWeight: "600",
  cursor: "pointer",
  transition: "0.3s",
};

const refreshButtonHoverStyle = {
  background: "#1d4ed8",
  transform: "translateY(-2px)",
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
};

const errorRetryButtonHoverStyle = {
  background: "#1d4ed8",
};

const statsContainerStyle = {
  display: "grid",
  gridTemplateColumns:
    "repeat(auto-fit,minmax(220px,1fr))",
  gap: "20px",
  marginTop: "30px",
};

const cardStyle = {
  background: "white",
  borderRadius: "16px",
  padding: "25px",
  boxShadow:
    "0 4px 20px rgba(0,0,0,0.08)",
  border: "1px solid #e5e7eb",
};

const cardTitleStyle = {
  margin: 0,
  color: "#475569",
  fontSize: "16px",
};

const cardValueStyle = {
  marginTop: "15px",
  fontSize: "34px",
  fontWeight: "bold",
  color: "#111827",
};

const chartsWrapperStyle = {
  display: "grid",
  gridTemplateColumns:
    "repeat(auto-fit,minmax(500px,1fr))",
  gap: "24px",
  marginTop: "40px",
};

const chartCardStyle = {
  background: "white",
  borderRadius: "16px",
  padding: "20px",
  boxShadow:
    "0 4px 20px rgba(0,0,0,0.08)",
  border: "1px solid #e5e7eb",
};

const chartTitleStyle = {
  marginBottom: "20px",
  color: "#0f172a",
};

export default Dashboard;
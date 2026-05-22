import { useNavigate, useLocation } from "react-router-dom";

function AdminSidebar() {

  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    localStorage.removeItem("admin_token");
    navigate("/admin");
  };

  const menuItems = [
    {
      label: "Dashboard",
      path: "/admin/dashboard",
      icon: "📊"
    },
    {
      label: "Faculty Management",
      path: "/admin/faculty",
      icon: "👥"
    },
    {
      label: "Upload Documents",
      path: "/admin/upload",
      icon: "📄"
    }
  ];

  return (
    <div style={sidebarStyle}>
      <div style={headerStyle}>
        <h2 style={{ margin: 0 }}>Admin Panel</h2>
      </div>

      <nav style={navStyle}>
        {menuItems.map((item) => (
          <div
            key={item.path}
            onClick={() => navigate(item.path)}
            style={{
              ...menuItemStyle,
              ...(location.pathname === item.path
                ? activeMenuItemStyle
                : {})
            }}
          >
            <span style={{ fontSize: "20px", marginRight: "10px" }}>
              {item.icon}
            </span>
            <span>{item.label}</span>
          </div>
        ))}
      </nav>

      <div style={footerStyle}>
        <button
          onClick={handleLogout}
          style={logoutButtonStyle}
        >
          Logout
        </button>
      </div>
    </div>
  );
}

const sidebarStyle = {
  position: "fixed",
  left: 0,
  top: 0,
  width: "250px",
  height: "100vh",
  background: "#1e293b",
  color: "white",
  display: "flex",
  flexDirection: "column",
  boxShadow: "2px 0 10px rgba(0,0,0,0.2)"
};

const headerStyle = {
  padding: "20px",
  background: "#0f172a",
  borderBottom: "2px solid #2563eb",
  textAlign: "center"
};

const navStyle = {
  flex: 1,
  padding: "20px 0",
  overflowY: "auto"
};

const menuItemStyle = {
  padding: "15px 20px",
  cursor: "pointer",
  display: "flex",
  alignItems: "center",
  transition: "all 0.3s",
  color: "#cbd5e1",
  fontSize: "16px",
  borderLeft: "4px solid transparent",
  marginBottom: "5px"
};

const activeMenuItemStyle = {
  background: "#2563eb",
  color: "white",
  borderLeft: "4px solid #60a5fa"
};

const footerStyle = {
  padding: "20px",
  borderTop: "1px solid #334155"
};

const logoutButtonStyle = {
  width: "100%",
  padding: "10px",
  background: "#dc2626",
  color: "white",
  border: "none",
  borderRadius: "6px",
  cursor: "pointer",
  fontSize: "16px",
  transition: "0.3s"
};

export default AdminSidebar;

import AdminSidebar from "./AdminSidebar";

function AdminLayout({ children }) {
  return (
    <div style={containerStyle}>
      <AdminSidebar />
      <div style={contentStyle}>
        {children}
      </div>
    </div>
  );
}

const containerStyle = {
  display: "flex",
  minHeight: "100vh"
};

const contentStyle = {
  flex: 1,
  marginLeft: "250px",
  padding: "40px",
  background: "#f8fafc",
  overflowY: "auto"
};

export default AdminLayout;

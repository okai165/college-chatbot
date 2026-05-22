import { useNavigate } from "react-router-dom";
import AdminLayout from "../components/AdminLayout";

function AdminHome() {

  const navigate = useNavigate();

  return (
    <AdminLayout>
      <div>
        <h1 style={{ marginBottom: "40px", color: "#1e293b" }}>
          Welcome to Admin Panel
        </h1>

        <div style={cardContainer}>

          <div
            style={cardStyle}
            onClick={() => navigate("/admin/dashboard")}
          >
            <h2>📊 Dashboard</h2>
            <p>
              View chatbot analytics and statistics
            </p>
          </div>

          <div
            style={cardStyle}
            onClick={() => navigate("/admin/faculty")}
          >
            <h2>👥 Faculty Management</h2>
            <p>
              Add, update, and manage faculty schedules
            </p>
          </div>

          <div
            style={cardStyle}
            onClick={() => navigate("/admin/upload")}
          >
            <h2>📄 Upload Documents</h2>
            <p>
              Upload PDFs, DOCX, TXT and ingest automatically
            </p>
          </div>

        </div>
      </div>
    </AdminLayout>
  );
}


const cardContainer = {
  display: "flex",
  justifyContent: "flex-start",
  gap: "30px",
  flexWrap: "wrap"
};

const cardStyle = {
  width: "280px",
  padding: "30px",
  borderRadius: "12px",
  background: "white",
  color: "#1e293b",
  cursor: "pointer",
  boxShadow: "0 4px 15px rgba(0,0,0,0.1)",
  transition: "all 0.3s",
  border: "1px solid #e2e8f0"
};

cardStyle[":hover"] = {
  transform: "translateY(-5px)",
  boxShadow: "0 8px 25px rgba(37, 99, 235, 0.2)"
};

export default AdminHome;
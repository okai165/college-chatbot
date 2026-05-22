import { useEffect, useState } from "react";
import AdminLayout from "../components/AdminLayout";

function UploadDocuments() {

  const categories = [
    "Admission",
    "Exams",
    "Results",
    "Notice",
    "Timetable",
    "Faculty",
    "Misc"
  ];

  const [files, setFiles] = useState([]);
  const [category, setCategory] = useState("Admission");
  const [filterCategory, setFilterCategory] = useState("All");
  const [filterDays, setFilterDays] = useState("30");
  const [uploadedDocs, setUploadedDocs] = useState([]);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const fetchUploadedDocs = async () => {
    try {
      const res = await fetch(
        "http://127.0.0.1:8000/uploaded-documents"
      );
      const data = await res.json();
      setUploadedDocs(data.files || []);
    } catch (err) {
      console.log(err);
    }
  };

  useEffect(() => {
    fetchUploadedDocs();
  }, []);

  const filteredDocs = uploadedDocs.filter((doc) => {
    const categoryMatch =
      filterCategory === "All" ||
      doc.category === filterCategory;

    const daysMatch =
      filterDays === "All" ||
      (new Date() - new Date(doc.uploaded_at)) /
        (1000 * 60 * 60 * 24) <=
        Number(filterDays);

    return categoryMatch && daysMatch;
  });

  // =========================
  // HANDLE FILE SELECT
  // =========================
  const handleFileChange = (e) => {

    setFiles(e.target.files);
  };

  // =========================
  // UPLOAD FILES
  // =========================
  const uploadFiles = async () => {

    if (!files.length) {

      alert("Select files first");

      return;
    }

    const formData = new FormData();

    for (let i = 0; i < files.length; i++) {

      formData.append("files", files[i]);
    }

    formData.append("category", category);

    try {

      setLoading(true);

      const res = await fetch(
        "http://127.0.0.1:8000/upload-documents",
        {
          method: "POST",
          body: formData
        }
      );

      const data = await res.json();

      setMessage(data.message);
      fetchUploadedDocs();

    } catch (err) {

      console.log(err);

      setMessage("Upload failed");

    } finally {

      setLoading(false);
    }
  };

  return (
    <AdminLayout>

      <div style={pageStyle}>

        <h1 style={titleStyle}>
          Upload Documents
        </h1>

        <div style={cardStyle}>

          <p style={infoStyle}>
            Supported formats:
            PDF, DOCX, TXT, PPTX
          </p>

          <div style={formRowStyle}>
            <div style={fieldGroupStyle}>
              <label style={labelStyle} htmlFor="category">
                Document Category
              </label>
              <select
                id="category"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                style={selectStyle}
              >
                {categories.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <input
            type="file"
            multiple
            onChange={handleFileChange}
            style={inputStyle}
          />

          {files.length > 0 && (

            <div style={fileListStyle}>

              <h3 style={{ marginTop: 0 }}>
                Selected Files
              </h3>

              {[...files].map((file, index) => (

                <div
                  key={index}
                  style={fileItemStyle}
                >
                  {file.name}
                </div>

              ))}

            </div>
          )}

          <button
            onClick={uploadFiles}
            style={buttonStyle}
            disabled={loading}
          >
            {loading
              ? "Uploading..."
              : "Upload & Ingest"}
          </button>

          {message && (

            <p style={messageStyle}>
              {message}
            </p>

          )}

        </div>

        <div style={uploadsCardStyle}>
          <div style={filterRowStyle}>
            <div style={fieldGroupStyle}>
              <label style={labelStyle} htmlFor="filterCategory">
                Filter by Category
              </label>
              <select
                id="filterCategory"
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
                style={selectStyle}
              >
                <option value="All">All</option>
                {categories.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </div>

            <div style={fieldGroupStyle}>
              <label style={labelStyle} htmlFor="filterDays">
                Show last
              </label>
              <select
                id="filterDays"
                value={filterDays}
                onChange={(e) => setFilterDays(e.target.value)}
                style={selectStyle}
              >
                <option value="All">All days</option>
                <option value="7">7 days</option>
                <option value="30">30 days</option>
                <option value="90">90 days</option>
                <option value="180">180 days</option>
              </select>
            </div>
          </div>

          <h2 style={sectionTitleStyle}>Uploaded Documents</h2>

          {filteredDocs.length === 0 ? (
            <p style={emptyStateStyle}>
              No documents found for the selected filters.
            </p>
          ) : (
            <table style={uploadTableStyle}>
              <thead>
                <tr>
                  <th>File</th>
                  <th>Category</th>
                  <th>Uploaded At</th>
                </tr>
              </thead>
              <tbody>
                {filteredDocs.map((doc, index) => (
                  <tr key={`${doc.filename}-${index}`}>
                    <td>{doc.filename}</td>
                    <td>{doc.category}</td>
                    <td>{new Date(doc.uploaded_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

      </div>

    </AdminLayout>
  );
}

const pageStyle = {
  padding: "20px",
};

const titleStyle = {
  marginBottom: "20px",
};

const cardStyle = {
  background: "white",
  color: "#1e293b",
  padding: "30px",
  borderRadius: "12px",
  display: "flex",
  flexDirection: "column",
  gap: "20px",
  maxWidth: "650px",
  border: "1px solid #e2e8f0",
  boxShadow: "0 2px 10px rgba(0,0,0,0.08)"
};

const infoStyle = {
  margin: 0,
  color: "#475569",
  fontSize: "15px",
};

const inputStyle = {
  padding: "10px",
  border: "1px solid #cbd5e1",
  borderRadius: "8px",
};

const fileListStyle = {
  background: "#f8fafc",
  padding: "15px",
  borderRadius: "8px",
  border: "1px solid #e2e8f0",
  maxHeight: "200px",
  overflowY: "auto",
};

const fileItemStyle = {
  padding: "8px 10px",
  borderBottom: "1px solid #e2e8f0",
  fontSize: "14px",
};

const buttonStyle = {
  padding: "12px",
  background: "#2563eb",
  color: "white",
  border: "none",
  borderRadius: "8px",
  cursor: "pointer",
  fontSize: "16px",
  fontWeight: "600",
};

const messageStyle = {
  margin: 0,
  fontWeight: "600",
  color: "#16a34a",
};

const formRowStyle = {
  display: "grid",
  gap: "20px",
  marginBottom: "20px",
};

const filterRowStyle = {
  display: "grid",
  gap: "20px",
  gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
  marginBottom: "20px",
};

const fieldGroupStyle = {
  display: "flex",
  flexDirection: "column",
  gap: "8px",
};

const labelStyle = {
  fontSize: "14px",
  color: "#334155",
  fontWeight: "600",
};

const selectStyle = {
  padding: "10px",
  borderRadius: "8px",
  border: "1px solid #cbd5e1",
  background: "white",
  color: "#0f172a",
};

const uploadsCardStyle = {
  background: "white",
  color: "#1e293b",
  padding: "30px",
  borderRadius: "12px",
  marginTop: "30px",
  border: "1px solid #e2e8f0",
  boxShadow: "0 2px 10px rgba(0,0,0,0.08)",
};

const sectionTitleStyle = {
  margin: "0 0 16px",
  color: "#0f172a",
};

const emptyStateStyle = {
  color: "#475569",
};

const uploadTableStyle = {
  width: "100%",
  borderCollapse: "collapse",
};

const uploadTableCellStyle = {
  padding: "12px 14px",
  borderBottom: "1px solid #e2e8f0",
  textAlign: "left",
  color: "#1e293b",
};

const uploadTableHeaderStyle = {
  padding: "12px 14px",
  borderBottom: "2px solid #e2e8f0",
  textAlign: "left",
  color: "#1e293b",
  fontWeight: 600,
};

export default UploadDocuments;
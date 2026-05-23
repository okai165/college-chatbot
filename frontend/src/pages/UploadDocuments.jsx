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

  // NEW STATES
  const [previewContent, setPreviewContent] = useState("");
  const [previewFile, setPreviewFile] = useState("");
  const [showModal, setShowModal] = useState(false);

  // =========================
  // FETCH DOCUMENTS
  // =========================
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

  // =========================
  // FILTER
  // =========================
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

  // =========================
  // READ DOCUMENT
  // =========================
  const readDocument = async (filename) => {

    try {

      const res = await fetch(
        `http://127.0.0.1:8000/read-document/${filename}`
      );

      const data = await res.json();

      setPreviewFile(filename);

      setPreviewContent(
        data.content || "No content found"
      );

      setShowModal(true);

    } catch (err) {

      console.log(err);
    }
  };

  // =========================
  // DELETE DOCUMENT
  // =========================
  const deleteDocument = async (filename) => {

    const confirmDelete = window.confirm(
      `Delete ${filename} ?`
    );

    if (!confirmDelete) return;

    try {

      await fetch(
        `http://127.0.0.1:8000/delete-document/${filename}`,
        {
          method: "DELETE"
        }
      );

      fetchUploadedDocs();

    } catch (err) {

      console.log(err);
    }
  };

  return (
    <AdminLayout>

      <div style={pageStyle}>

        <h1
          style={titleStyle}
          onMouseEnter={(e) => {
            e.target.style.transform = "scale(1.03)";
            e.target.style.color = "#2563eb";
            e.target.style.textShadow =
              "0 4px 12px rgba(37,99,235,0.25)";
        }}
        onMouseLeave={(e) => {
          e.target.style.transform = "scale(1)";
          e.target.style.color = "#0f172a";
          e.target.style.textShadow = "none";
        }}
      >
        Upload Documents
      </h1>

        <div style={cardStyle}>

          <p style={infoStyle}>
            Supported formats:
            PDF, DOCX, TXT
          </p>

          <div style={formRowStyle}>

            <div style={fieldGroupStyle}>

              <label style={labelStyle}>
                Document Category
              </label>

              <select
                value={category}
                onChange={(e) =>
                  setCategory(e.target.value)
                }
                style={selectStyle}
              >

                {categories.map((item) => (

                  <option
                    key={item}
                    value={item}
                  >
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

              <h3>
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

        {/* ========================= */}
        {/* DOCUMENTS TABLE */}
        {/* ========================= */}

        <div style={uploadsCardStyle}>

          <div style={filterRowStyle}>

            <div style={fieldGroupStyle}>

              <label style={labelStyle}>
                Filter by Category
              </label>

              <select
                value={filterCategory}
                onChange={(e) =>
                  setFilterCategory(e.target.value)
                }
                style={selectStyle}
              >

                <option value="All">
                  All
                </option>

                {categories.map((item) => (

                  <option
                    key={item}
                    value={item}
                  >
                    {item}
                  </option>

                ))}

              </select>

            </div>

            <div style={fieldGroupStyle}>

              <label style={labelStyle}>
                Show Last
              </label>

              <select
                value={filterDays}
                onChange={(e) =>
                  setFilterDays(e.target.value)
                }
                style={selectStyle}
              >

                <option value="All">
                  All Days
                </option>

                <option value="7">
                  7 Days
                </option>

                <option value="30">
                  30 Days
                </option>

                <option value="90">
                  90 Days
                </option>

              </select>

            </div>

          </div>

          <h2 style={sectionTitleStyle}>
            Uploaded Documents
          </h2>

          {filteredDocs.length === 0 ? (

            <p>No documents found.</p>

          ) : (

            <table style={uploadTableStyle}>

              <thead>

                <tr>

                  <th style={uploadTableHeaderStyle}>
                    File
                  </th>

                  <th style={uploadTableHeaderStyle}>
                    Category
                  </th>

                  <th style={uploadTableHeaderStyle}>
                    Uploaded
                  </th>

                  <th style={uploadTableHeaderStyle}>
                    Actions
                  </th>

                </tr>

              </thead>

              <tbody>

                {filteredDocs.map((doc, index) => (

                  <tr key={index}>

                    <td
                      style={{
                        ...uploadTableCellStyle,
                        ...fileNameCellStyle
                      }}
                    >
                      {doc.filename}
                    </td>
                      
                    

                    <td style={uploadTableCellStyle}>
                      {doc.category}
                    </td>

                    <td style={uploadTableCellStyle}>
                      {new Date(
                        doc.uploaded_at
                      ).toLocaleString()}
                    </td>
                      <td style={uploadTableCellStyle}>
                      
                        <div style={actionButtonsWrapperStyle}>
                      
                          <button
                            style={{
                              ...readButtonStyle,
                              ...actionButtonStyle
                            }}
                            onClick={() =>
                              readDocument(doc.filename)
                            }
                          >
                            Read
                          </button>
                      
                          <button
                            style={{
                              ...deleteButtonStyle,
                              ...actionButtonStyle
                            }}
                            onClick={() =>
                              deleteDocument(doc.filename)
                            }
                          >
                            Delete
                          </button>
                      
                        </div>
                      
                      </td>

                    

                  </tr>

                ))}

              </tbody>

            </table>

          )}

        </div>

        {/* ========================= */}
        {/* MODAL */}
        {/* ========================= */}

        {showModal && (

          <div style={modalOverlayStyle}>

            <div style={modalStyle}>

              <div style={modalHeaderStyle}>

                <h2>
                  {previewFile}
                </h2>

                <button
                  onClick={() =>
                    setShowModal(false)
                  }
                  style={closeButtonStyle}
                >
                  X
                </button>

              </div>

              <div style={modalContentStyle}>
                {previewContent}
              </div>

            </div>

          </div>

        )}

      </div>

    </AdminLayout>
  );
}

const pageStyle = {
  padding: "20px",
};

const titleStyle = {
  marginBottom: "20px",
  color: "#0f172a",
  fontSize: "34px",
  fontWeight: "700",
  letterSpacing: "0.5px",
  transition: "all 0.3s ease",
  cursor: "pointer",
  display: "inline-block",
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
};

const infoStyle = {
  margin: 0,
};

const inputStyle = {
  padding: "10px",
};

const fileListStyle = {
  background: "#f8fafc",
  padding: "15px",
  borderRadius: "8px",
};

const fileItemStyle = {
  padding: "6px 0",
};

const buttonStyle = {
  padding: "12px",
  background: "#2563eb",
  color: "white",
  border: "none",
  borderRadius: "8px",
  cursor: "pointer",
};

const messageStyle = {
  color: "green",
};

const formRowStyle = {
  display: "grid",
  gap: "20px",
};

const filterRowStyle = {
  display: "flex",
  gap: "20px",
  marginBottom: "20px",
};

const fieldGroupStyle = {
  display: "flex",
  flexDirection: "column",
  gap: "8px",
};

const labelStyle = {
  fontWeight: "600",
};

const selectStyle = {
  padding: "10px",
  borderRadius: "8px",
};

const uploadsCardStyle = {
  marginTop: "30px",
  background: "white",
  padding: "30px",
  borderRadius: "12px",
};

const sectionTitleStyle = {
  marginBottom: "20px",
};

const uploadTableStyle = {
  width: "100%",
  borderCollapse: "collapse",
};

const uploadTableCellStyle = {
  padding: "12px",
  borderBottom: "1px solid #ddd",
  verticalAlign: "top",
  wordBreak: "break-word",
};

const uploadTableHeaderStyle = {
  padding: "12px",
  borderBottom: "2px solid #ddd",
  textAlign: "left",
};
const fileNameCellStyle = {
  maxWidth: "320px",
  whiteSpace: "normal",
  overflowWrap: "break-word",
  lineHeight: "1.5",
};

const actionButtonsWrapperStyle = {
  display: "flex",
  gap: "8px",
  flexWrap: "wrap",
  alignItems: "center",
  minWidth: "160px",
};

const actionButtonStyle = {
  minWidth: "70px",
  textAlign: "center",
};

const readButtonStyle = {
  background: "#2563eb",
  color: "white",
  border: "none",
  padding: "8px 12px",
  borderRadius: "6px",
  marginRight: "10px",
  cursor: "pointer",
};

const deleteButtonStyle = {
  background: "#dc2626",
  color: "white",
  border: "none",
  padding: "8px 12px",
  borderRadius: "6px",
  cursor: "pointer",
};

const modalOverlayStyle = {
  position: "fixed",
  top: 0,
  left: 0,
  width: "100%",
  height: "100%",
  background: "rgba(0,0,0,0.5)",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
};

const modalStyle = {
  background: "white",
  width: "80%",
  maxWidth: "900px",
  borderRadius: "12px",
  padding: "20px",
  maxHeight: "80vh",
  overflow: "hidden",
};

const modalHeaderStyle = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
};

const closeButtonStyle = {
  background: "red",
  color: "white",
  border: "none",
  padding: "8px 12px",
  borderRadius: "6px",
  cursor: "pointer",
};

const modalContentStyle = {
  marginTop: "20px",
  maxHeight: "60vh",
  overflowY: "auto",
  whiteSpace: "pre-wrap",
  lineHeight: "1.6",
};

export default UploadDocuments;
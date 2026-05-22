import { useEffect, useState } from "react";
import AdminLayout from "../components/AdminLayout";

function FacultyManager() {

  const [faculty, setFaculty] = useState([]);

  const [formData, setFormData] = useState({
    faculty_name: "",
    subject_name: "",
    time_slot: "",
    room_number: ""
  });

  const [editingId, setEditingId] = useState(null);

  // =========================
  // FETCH FACULTY
  // =========================
  const fetchFaculty = async () => {

    try {

      const res = await fetch(
        "http://127.0.0.1:8000/faculty"
      );

      const data = await res.json();

      setFaculty(data);

    } catch (err) {

      console.log(err);
    }
  };

  useEffect(() => {

    fetchFaculty();

  }, []);

  // =========================
  // HANDLE INPUT
  // =========================
  const handleChange = (e) => {

    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  // =========================
  // ADD OR UPDATE
  // =========================
  const handleSubmit = async () => {

    try {

      // UPDATE
      if (editingId) {

        await fetch(
          `http://127.0.0.1:8000/faculty/${editingId}`,
          {
            method: "PUT",
            headers: {
              "Content-Type": "application/json"
            },
            body: JSON.stringify(formData)
          }
        );

      }

      // ADD
      else {

        await fetch(
          "http://127.0.0.1:8000/faculty",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json"
            },
            body: JSON.stringify(formData)
          }
        );
      }

      // RESET
      setFormData({
        faculty_name: "",
        subject_name: "",
        time_slot: "",
        room_number: ""
      });

      setEditingId(null);

      fetchFaculty();

    } catch (err) {

      console.log(err);
    }
  };

  // =========================
  // DELETE
  // =========================
  const deleteFaculty = async (id) => {

    try {

      await fetch(
        `http://127.0.0.1:8000/faculty/${id}`,
        {
          method: "DELETE"
        }
      );

      fetchFaculty();

    } catch (err) {

      console.log(err);
    }
  };

  // =========================
  // EDIT
  // =========================
  const editFaculty = (item) => {

    setEditingId(item.id);

    setFormData({
      faculty_name: item.faculty_name,
      subject_name: item.subject_name,
      time_slot: item.time_slot,
      room_number: item.room_number || ""
    });
  };

  return (
    <AdminLayout>
      <div style={pageStyle}>

      <h1 style={titleStyle}>Faculty Management</h1>

      {/* ================= FORM ================= */}

      <div style={formStyle}>

        <input
          name="faculty_name"
          placeholder="Faculty Name"
          value={formData.faculty_name}
          onChange={handleChange}
          style={inputStyle}
        />

        <input
          name="subject_name"
          placeholder="Subject"
          value={formData.subject_name}
          onChange={handleChange}
          style={inputStyle}
        />

        <input
          name="time_slot"
          placeholder="Time Slot"
          value={formData.time_slot}
          onChange={handleChange}
          style={inputStyle}
        />

        <input
          name="room_number"
          placeholder="Room / Lab (Optional)"
          value={formData.room_number}
          onChange={handleChange}
          style={inputStyle}
        />

        <button
          onClick={handleSubmit}
          style={buttonStyle}
        >
          {editingId ? "Update Faculty" : "Add Faculty"}
        </button>

      </div>

      {/* ================= TABLE ================= */}

      <table style={tableStyle}>

        <thead>

          <tr>
            <th>Faculty</th>
            <th>Subject</th>
            <th>Time Slot</th>
            <th>Room</th>
            <th>Actions</th>
          </tr>

        </thead>

        <tbody>

          {faculty.map((item) => (

            <tr key={item.id}>

              <td>{item.faculty_name}</td>

              <td>{item.subject_name}</td>

              <td>{item.time_slot}</td>

              <td>{item.room_number || "-"}</td>

              <td>

                <button
                  onClick={() => editFaculty(item)}
                  style={editButton}
                >
                  Edit
                </button>

                <button
                  onClick={() => deleteFaculty(item.id)}
                  style={deleteButton}
                >
                  Delete
                </button>

              </td>

            </tr>
          ))}

        </tbody>

      </table>

      </div>
    </AdminLayout>
  );
}


// =========================
// STYLES
// =========================

const formStyle = {
  display: "grid",
  gap: "15px",
  background: "white",
  padding: "20px",
  borderRadius: "10px",
  marginTop: "20px"
};

const inputStyle = {
  padding: "10px",
  borderRadius: "6px",
  border: "1px solid #ccc",
  fontSize: "14px",
  background: "white",
  color: "#0f172a"
};

const pageStyle = {
  padding: "20px"
};

const titleStyle = {
  marginBottom: "20px",
  color: "#0f172a"
};

const buttonStyle = {
  padding: "12px",
  background: "#2563eb",
  color: "white",
  border: "none",
  borderRadius: "6px",
  cursor: "pointer"
};

const tableStyle = {
  width: "100%",
  marginTop: "30px",
  background: "white",
  color: "#1e293b",
  borderCollapse: "collapse",
  borderRadius: "10px",
  overflow: "hidden",
  border: "1px solid #e2e8f0"
};

const editButton = {
  marginRight: "10px",
  padding: "6px 10px",
  background: "#16a34a",
  color: "white",
  border: "none",
  borderRadius: "4px",
  cursor: "pointer"
};

const deleteButton = {
  padding: "6px 10px",
  background: "#dc2626",
  color: "white",
  border: "none",
  borderRadius: "4px",
  cursor: "pointer"
};

export default FacultyManager;
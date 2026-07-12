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
  const [departments, setDepartments] = useState([]);
  const [selectedDepartment, setSelectedDepartment] = useState("");
  const [editingId, setEditingId] = useState(null);
  // =========================
  // FETCH DEPARTMENTS
  // =========================
  const fetchDepartments = async () => {

    try {

      const res = await fetch(
        "http://127.0.0.1:8000/departments"
      );

      const data = await res.json();

      setDepartments(data);

    } catch (err) {

      console.log(err);

    }

  };
  // =========================
  // FETCH FACULTY
  // =========================
  const fetchFaculty = async (departmentId) => {

    if (!departmentId) return;

    try {

      const res = await fetch(
        `http://127.0.0.1:8000/faculty?department_id=${departmentId}`
      );

      const data = await res.json();

      setFaculty(data);

    } catch (err) {

      console.log(err);

    }

  };

  useEffect(() => {

    fetchDepartments();

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
    if (!selectedDepartment) {
      alert("Please select a department first.");
      return;
    }
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
            body: JSON.stringify({
              ...formData,
              department_id: selectedDepartment
            })
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

      fetchFaculty(selectedDepartment);

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

      fetchFaculty(selectedDepartment);

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

      <select
          value={selectedDepartment}
          onChange={(e) => {
            const id = e.target.value;
            setSelectedDepartment(id);
            fetchFaculty(id);
          }}
          style={selectStyle}
        >
          <option value="">Select Department</option>

          {departments.map((dept) => (
            <option key={dept.id} value={dept.id}>
              {dept.department_name}
            </option>
          ))}
      </select>

      {/* Show only after department selection */}

      {selectedDepartment && (
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
              placeholder="Room / Lab"
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
      )}

      {/* Show table only after department selection */}

      {selectedDepartment && (
        <table style={tableStyle}>

            <thead>
              <tr style={{
                      background: "#f8fafc",
                      height: "55px"
                  }}
              >
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

                  <td style={{
                          padding: "18px",
                          textAlign: "center",
                          borderBottom: "1px solid #e5e7eb"
                      }}
                  >{item.faculty_name}</td>
                  <td style={{
                          padding: "18px",
                          textAlign: "center",
                          borderBottom: "1px solid #e5e7eb"
                      }}
                  >{item.subject_name}</td>
                  <td style={{
                          padding: "18px",
                          textAlign: "center",
                          borderBottom: "1px solid #e5e7eb"
                      }}
                  >{item.time_slot}</td>
                  <td style={{
                          padding: "18px",
                          textAlign: "center",
                          borderBottom: "1px solid #e5e7eb"
                      }}
                  >{item.room_number || "-"}</td>

                  <td style={{
                          padding: "18px",
                          textAlign: "center",
                          borderBottom: "1px solid #e5e7eb"
                      }} 
                  >

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
      )}
      
      </div>
    </AdminLayout>
  );
}


// =========================
// STYLES
// =========================
const formStyle = {
  background: "#fff",
  borderRadius: "12px",
  padding: "25px",
  display: "grid",
  gap: "18px",
  marginBottom: "35px",
  boxShadow: "0 2px 10px rgba(172, 197, 182, 0.08)"
};

const inputStyle = {
   width: "100%",
  padding: "14px",
  borderRadius: "8px",
  border: "1px solid #cbd5e1",
  backgroundColor: "#eff6ff",   // Light blue
  color: "#0f172a",
  fontSize: "15px",
  outline: "none",
  boxSizing: "border-box"
};

const pageStyle = {
  padding: "35px",
  maxWidth: "1100px",
  margin: "0 auto"
};

const titleStyle = {
  fontSize: "48px",
  fontWeight: "700",
  marginBottom: "25px",
  color: "#0f172a"
};

const buttonStyle = {
  padding: "14px",
  borderRadius: "8px",
  background: "#2563eb",
  color: "#fff",
  border: "none",
  cursor: "pointer",
  fontSize: "16px",
  fontWeight: "600"
};

const tableStyle = {
  width: "100%",
  background: "#fff",
  borderRadius: "12px",
  overflow: "hidden",
  borderCollapse: "collapse",
  boxShadow: "0 2px 10px rgba(0,0,0,.08)"
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
const selectStyle = {
  width: "420px",
  padding: "12px",
  marginBottom: "25px",
  borderRadius: "8px",
  border: "1px solid #d1d5db",
  fontSize: "16px",
  backgroundColor: "#ffffff",
  color: "#0f172a",
  outline: "none"
};
export default FacultyManager;
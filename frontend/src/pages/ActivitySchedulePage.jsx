import { useNavigate } from "react-router-dom";

export default function AdmissionUpdatesPage() {

  const navigate = useNavigate();

  return (
    <div className="page-container">

      <button
        onClick={() => navigate("/")}
      >
        ← Back
      </button>

      <h1>Activity Schedule</h1>

      <p>
        Admission notifications will appear here.
      </p>

    </div>
  );
}
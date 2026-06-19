import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

export default function AdmissionsPage() {

  const [items, setItems] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {

    fetch("http://localhost:8000/admissions")
      .then(res => res.json())
      .then(data => setItems(data));

  }, []);

  return (
    <div className="page-container">

      <button
        onClick={() => navigate("/")}
      >
        ← Back
      </button>

      <h1>Admissions Information</h1>

      {items.map(item => (

        <div
          key={item.id}
          className="notification-card"
        >

          <h2>{item.title}</h2>

          <p>{item.summary}</p>

          {item.start_date && (
            <p>
              <strong>Start Date:</strong>
              {item.start_date}
            </p>
          )}

          {item.last_date && (
            <p>
              <strong>Last Date:</strong>
              {item.last_date}
            </p>
          )}

          {item.eligibility && (
            <p>
              <strong>Eligibility:</strong>
              {item.eligibility}
            </p>
          )}

        </div>

      ))}

      <button
        onClick={() => navigate("/chat")}
      >
        Ask AI About Admissions
      </button>

    </div>
  );
}
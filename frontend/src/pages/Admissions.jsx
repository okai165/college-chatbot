import { useEffect, useState } from "react";

function Admissions() {

  const [notifications,setNotifications] =
    useState([]);

  useEffect(() => {

    fetch(
      "http://127.0.0.1:8000/notifications?category=Admission"
    )
      .then(res => res.json())
      .then(data => setNotifications(data));

  }, []);

  return (
    <div>

      <button>
        ← Back
      </button>

      <h1>
        Admissions
      </h1>

      {notifications.map((item) => (

        <div
          key={item.id}
          className="notification-card"
        >

          <h2>{item.title}</h2>

          <p>
            {item.summary}
          </p>

          <p>
            Start Date:
            {item.start_date}
          </p>

          <p>
            Last Date:
            {item.last_date}
          </p>

          <p>
            Eligibility:
            {item.eligibility}
          </p>

        </div>

      ))}

      <button>
        🤖 Ask AI About Admissions
      </button>

    </div>
  );
}

export default Admissions;